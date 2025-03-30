Agentic AI Recruiter Bot - Project Overview
===========================================

Description:
-------------
This project implements an agentic recruiter bot capable of conducting multi-turn voice-based interviews over Google Meet. It uses natural language interaction, question-answering, and summarization—all orchestrated through LangGraph state machines.

Dependencies:
-------------
- Python 3.10+
- `langchain`, `langgraph`, `pydantic`, `streamlit`
- `whisper` (for speech-to-text)
- `pyttsx3` (text-to-speech)
- `sounddevice`, `numpy`, `wave` (audio recording)
- `selenium` (for automated Google Meet joining)
- Chrome browser with a user profile preconfigured
- Ollama with the "mistral" model installed locally

Architecture:
-------------
The system is broken into 3 separate LangGraph subgraphs, each with its own state machine:

1. **Graph 1: Skill Extraction and Question Generation**
   - Takes a job description
   - Extracts relevant skills
   - Generates a list of interview questions based on those skills

2. **Graph 2: Multi-turn Interview with Human-in-the-loop**
   - Asks questions one by one
   - Waits for a voice response
   - Triggers a LangGraph interrupt to allow human confirmation or correction of the answer
   - Uses checkpointing to resume from the "respond" node after each correction

3. **Graph 3: Summarization**
   - Summarizes the entire transcript
   - Gives a final score out of 10 based on the candidate's responses

Key Decisions Made:
-------------------
- Used **Ollama + Mistral** as the local LLM backend for question generation and response evaluation
- Implemented each stage as a **separate LangGraph** to allow clear checkpointing and state management
- Used **LangGraph interrupts** for human-in-the-loop answer revision before continuing the conversation
- Applied **MemorySaver checkpointing** to ensure state persistence between turns
- Designed the graphs so that interruptions always resume from the `respond` node (not from the beginning)

Notes:
------
- Voice interaction is handled using Whisper and TTS
- Google Meet joining is fully automated using Selenium
- Job descriptions are read from a `.txt` file
