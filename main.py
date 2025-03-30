import streamlit as st
import subprocess
import os
from agent.voice import transcribe_audio, speak
from agent.meet_integration import schedule_meet
import datetime

st.title("🤖 Recruiter Bot")

# === Schedule Instant Google Meet & Start Interview Bot ===
if st.button("Run Interview"):
    st.info("📅 Scheduling a Google Meet...")
    meet_link = "https://meet.google.com/new"
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
selected_date = st.date_input("Pick a date", datetime.date.today())
selected_time = st.time_input("Pick a time", datetime.datetime.now().time())

scheduled_datetime = datetime.datetime.combine(selected_date, selected_time)

if st.button("Schedule Meet Only"):
    scheduled_datetime = datetime.datetime.combine(selected_date, selected_time)
    now = datetime.datetime.now()

    if scheduled_datetime <= now:
        st.error("Please select a time in the future!")
    else:
        link = "https://meet.google.com/new"  # Replace if needed
        st.success(f"✅ Meet scheduled for {scheduled_datetime.strftime('%A, %d %B %Y at %I:%M %p')}")
        st.markdown(f"🔗 [Join here]({link})")

        wait_seconds = (scheduled_datetime - now).total_seconds()

        with st.spinner(f"Waiting until {scheduled_datetime.strftime('%I:%M %p')} to start the bot..."):
            time.sleep(wait_seconds)

        # Launch your main process
        subprocess.Popen(["python", "meet_bot_pipeline.py"], cwd=os.getcwd())
        st.success("🚀 Meet bot started!")


