import time
import sounddevice as sd
import numpy as np
import wave
import whisper
import os
import pyttsx3
from agent.recruiter_graph import recruiter_graph1, recruiter_graph2, recruiter_graph3
from selenium import webdriver
from selenium.webdriver.common.by import By
import threading
from dateparser import parse
from agent.meet_integration import RecruiterState
from langgraph.types import Command, interrupt
# from langgraph.pregel import Signal

# === SETUP ===
SAMPLE_RATE = 16000
RECORD_SECONDS = 7
WHISPER_MODEL = "base"
TTS_ENGINE = pyttsx3.init()
TTS_ENGINE.setProperty('rate', 200)
DEVICE_INDEX = 2
# state = ""
# === AUDIO ===
def record_audio(filename="audio.wav", duration=RECORD_SECONDS):
    print("🎙️ Recording...")
    # print(sd.query_devices()) 
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16', device=DEVICE_INDEX)
    sd.wait()
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio.tobytes())
    print(f"🎧 Saved audio to {filename}")
    return filename

def transcribe_audio(filename):
    try:
        abs_path = os.path.abspath(filename)
        print(f"📝 Transcribing: {abs_path}")
        model = whisper.load_model("base")
        result = model.transcribe(abs_path)
        print("🗣️ Transcribed:", result["text"])
        # state.answer = result["text"]
        # print(f'Answer variable in transcribe: {state.answer}')
        return result["text"]
    except Exception as e:
        print("❌ Whisper error:", e)
        # state.answer = ""
        return ""

# === TTS ===
def speak(text):
    print(f"🔊 {text}")
    #removing the question number
    if len(text)>2 and text[1] == '.':
        text = text[2:]
    TTS_ENGINE.say(text)
    TTS_ENGINE.runAndWait()

# === JOIN MEET ===
def join_google_meet(meet_url):
    def run():
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        options = Options()
        options.add_argument("--user-data-dir=C:\\AgentBotProfile")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("--remote-debugging-port=9222")

        driver = webdriver.Chrome(options=options)
        driver.get(meet_url)

        print("✅ Chrome opened with bot profile. Waiting for Meet to load...")
        time.sleep(8)

        try:
            camera_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@role='button'][@aria-label[contains(., 'camera') or contains(., 'Camera')]]")
                )
            )
            camera_button.click()
            print("📷 Camera turned off")
            join_button = driver.find_element(By.XPATH, "//button[contains(., 'Join now')]")
            join_button.click()
            print("✅ Clicked 'Join now'")
        except Exception as e:
            print("❌ Could not find 'Join now' button:", e)

        # Keep Chrome session alive
        while True:
            time.sleep(1)

    threading.Thread(target=run, daemon=True).start()

# === INTENT DETECTION ===
def detect_reschedule_intent(text):
    keywords = ["later", "tomorrow", "next", "reschedule", "another time"]
    return any(kw in text.lower() for kw in keywords)

def extract_datetime(text):
    return parse(text)

def run_loop(jd_text, meet_url):
    join_google_meet(meet_url)

    # Wait for hello
    while True:
        speak("Waiting for you to say 'hello' to begin...")
        file = record_audio("hello.wav")
        msg = transcribe_audio(file)
        if "hello" in msg.lower():
            speak("Hi! Are you ready to begin the interview or would you like to reschedule?")
            break

    # Wait for response
    file = record_audio("ready.wav")
    response = transcribe_audio(file)
    if detect_reschedule_intent(response):
        dt = extract_datetime(response)
        if dt:
            speak(f"Okay, I will reschedule your interview for {dt.strftime('%A at %I:%M %p')}")
            print("📅 Rescheduled for:", dt)
            return
        else:
            speak("I heard you'd like to reschedule, but couldn't understand the time. Please repeat.")
            return

    # Proceed with interview
    speak("Great, let's begin!")


    config1 = {
    "configurable": {
        "thread_id": "user-session-123"
        }
    }   
    config2 = {
    "configurable": {
        "thread_id": "user-session-124"
        }
    }   
    config3 = {
    "configurable": {
        "thread_id": "user-session-125"
        }
    }   
    #extract skills graph
    state1 = RecruiterState(job_description=jd_text)
    for step in recruiter_graph1.stream(state1, config=config1):
        current_node = next(iter(step))
        node_output = step[current_node]
        if "summary" in node_output:
            state1.summary = node_output["summary"]
        if "questions" in node_output:
            state1.questions = node_output["questions"]

    snapshot = recruiter_graph1.get_state(config1)
    print('snapshot1----------------:')
    {k: v for k, v in snapshot.values.items() if k in ("summary")}
    

    #question-answer graph
    state2 = RecruiterState(
    job_description=jd_text,
    summary=state1.summary or "",       # empty string fallback
    questions=state1.questions or []    # empty list fallback
)
    print(f'state2: {state2}')

    qa_index = 3
    while qa_index:
        # Stream steps from graph
        for step in recruiter_graph2.stream(state2, config=config2):
            print("STEP:", step)
            current_node = next(iter(step))
            node_output = step[current_node]

            # Show current question index
            print(f'++++++++++++++++++++++++updated_question_index: {state2.question_index}')

            if current_node == "ask_question":
                continue  # wait until respond

            elif current_node == "respond":
                response = node_output["response"]
                state2.transcript = node_output["transcript"]
                speak(response)

        current_q_index = state2.question_index
        question = state2.questions[current_q_index]
        state2.current_question = question
        print(f'-----------question {current_q_index}: {state2.current_question}')

        speak(question)
        file = record_audio("answer.wav", 30)
        updated = transcribe_audio(file)
        
        # updated = input("📝 Your updated answer: ")

        # Update state using the graph's update_state
        recruiter_graph2.update_state(config2, {
            "answer": updated,
            "question_index": current_q_index + 1,  # advance manually here
            "transcript": state2.transcript + [{"q": state2.current_question, "a": updated}]
        })

        # Resume execution from interrupt
        updated_state_dict = recruiter_graph2.invoke(Command(resume=True), config=config2)

        # Rebuild state2 from the updated dict
        state2 = RecruiterState(**updated_state_dict)

        qa_index -= 1




    
    print(f'state2--------------------------: {state2}')

    state3 = RecruiterState(
        transcript = state2.transcript,
        job_description = state2.job_description,
        )
    for step in recruiter_graph3.stream(state3, config=config3):
        current_node = next(iter(step))
        node_output = step[current_node]
        print(step)
        if "summary" in node_output:
            state3.summary = node_output["summary"]
        if "questions" in node_output:
            state3.questions = node_output["questions"]
    speak(state3.summary)
    print(f'state2 summary: {state2.summary}')

    input("🛑 Press Enter to exit...")


if __name__ == "__main__":
    jd = open("data/job_description.txt").read()
    meet_url = "https://meet.google.com/new"
    # meet_url = "https://meet.google.com/wrp-rzmy-ezn"
    # state = RecruiterState(job_description=jd)
    run_loop(jd, meet_url)
