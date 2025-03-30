import streamlit as st
import subprocess
import os
from agent.voice import transcribe_audio, speak
from agent.meet_integration import schedule_meet

st.title("🤖 Recruiter Bot")

# === Schedule Instant Google Meet & Start Interview Bot ===
if st.button("Run Interview"):
    st.info("📅 Scheduling a Google Meet...")
    # meet_link = "https://meet.google.com/new"  # Using direct Meet URL since service accounts can't auto-create links without Workspace
    meet_link = "https://meet.google.com/wrp-rzmy-ezn"
    st.success(f"✅ Meet scheduled: [Join here]({meet_link})")

    # Launch the real-time Meet bot as a subprocess
    st.info("🤖 Launching voice agent to join Meet and wait for greeting...")
    subprocess.Popen(["python", "meet_bot_pipeline.py"], cwd=os.getcwd())

    st.warning("The bot will start responding once the candidate says 'hello'.")

# === Upload Audio Transcription ===
uploaded = st.file_uploader("Upload Audio", type="mp3")
if uploaded:
    text = transcribe_audio(uploaded)
    st.write("📝 Transcription:", text)

# === Standalone Meet Scheduler (optional) ===
if st.button("Schedule Meet Only"):
    link = "https://meet.google.com/new"  # Using generic Meet link for personal accounts
    st.success(f"Meet scheduled: [Join here]({link})")

