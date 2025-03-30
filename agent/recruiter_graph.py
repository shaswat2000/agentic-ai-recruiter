from langgraph.graph import StateGraph, END
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms import Ollama
from agent.meet_integration import RecruiterState
from langchain_core.runnables import RunnableLambda
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt


llm = Ollama(model="mistral")

extract_chain = LLMChain(llm=llm, prompt=PromptTemplate(
    input_variables=["job_description"],
    template="Extract key skills from: {job_description}"
))

question_chain = LLMChain(llm=llm, prompt=PromptTemplate(
    input_variables=["skills_summary"],
    template="""Generate exactly 3 interview questions based on the given skills: {skills_summary}. 
    Separate each question with a newline character."""
))

respond_chain = LLMChain(llm=llm, prompt=PromptTemplate(
    input_variables=["question", "answer"],
    template="""
    Question: {question}
    Candidate's Answer: {answer}

    Acknowledge the candidate's answer in a single sentence.
    """
))

summarize_chain = LLMChain(llm=llm, prompt=PromptTemplate(
    input_variables=["transcript"],
    template="Thank the candidate for the interview, and let them know we'll get back to them with any updates as soon as possible. Also give a score for the interview out of 10, based on the answers to questions in the transcript: {transcript}."
))

# === Graph nodes ===
def extract_skills(state):
    summary = extract_chain.run(job_description=state.job_description)
    return {"summary": summary}

def generate_questions(state):
    questions = question_chain.run(skills_summary=state.summary, config={"max_tokens": 30})
    question_list = [q.strip() for q in questions.split("\n") if q.strip()]
    return {"questions": question_list, "question_index": 0, "transcript": []}

def ask_question_node(state):
    # state.current_question = state.questions[state.question_index]
    # state.transcript = state.transcript + [{"q": state.current_question}]
    answer = interrupt({
        "prompt": "Interrputing to modify answer",
        "answer": state.answer,
        "question_index": state.question_index,
        "transcript": state.transcript
    })
    i = state.question_index
    return {"current_question": state.questions[i]}

def respond_node(state):
    response = ""
    if(state.question_index>0):
        response = respond_chain.run(
            question=state.current_question,
            answer=state.answer,
            config={"max_tokens": 5}
        )
    return {"response": response, "transcript": state.transcript}

def should_continue_node(state):
    i = state.question_index
    if i + 1 < len(state.questions):
        return {"question_index": i + 1, "next": "ask_question"}
    else:
        return {"next": "summarize"}

def summarize_node(state):
    convo = "\n".join([f"Q: {x['q']}\nA: {x['a']}" for x in state.transcript])
    summary = summarize_chain.run(transcript=convo)
    return {"summary": summary}

# === Build LangGraphs ===
graph1 = StateGraph(state_schema=RecruiterState)
graph3 = StateGraph(state_schema=RecruiterState)
graph2 = StateGraph(state_schema=RecruiterState)

# Nodes
graph1.add_node("extract_skills", extract_skills)
graph1.add_node("generate_questions", generate_questions)
graph2.add_node("ask_question", ask_question_node)
graph2.add_node("respond", respond_node)
graph3.add_node("summarize", summarize_node)

# Edges
graph1.set_entry_point("extract_skills")
graph1.add_edge("extract_skills", "generate_questions")
graph1.add_edge("generate_questions", END)

graph2.set_entry_point("respond")
graph2.add_edge("respond", "ask_question")
graph2.add_edge("ask_question", END)

graph3.set_entry_point("summarize")
graph3.add_edge("summarize", END)


checkpointer1 = MemorySaver()
checkpointer2 = MemorySaver()
checkpointer3 = MemorySaver()

recruiter_graph1 = graph1.compile(checkpointer=checkpointer1)
recruiter_graph2 = graph2.compile(checkpointer=checkpointer2)
recruiter_graph3 = graph3.compile(checkpointer=checkpointer3)
