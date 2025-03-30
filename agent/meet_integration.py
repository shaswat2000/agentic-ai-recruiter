from google.oauth2 import service_account
from googleapiclient.discovery import build
from pydantic import BaseModel
from datetime import datetime, timedelta
import pytz
from typing import Optional

def schedule_meet(candidate_email="test@example.com"):
    credentials = service_account.Credentials.from_service_account_file(
        "google_creds.json",
        scopes=["https://www.googleapis.com/auth/calendar"]
    )
    service = build("calendar", "v3", credentials=credentials)
    now = datetime.now(pytz.timezone('Asia/Kolkata'))
    start = now + timedelta(minutes=5)
    end = start + timedelta(minutes=30)
    event = {
        'summary': 'Recruiter Interview',
        'start': {'dateTime': start.isoformat(), 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end.isoformat(), 'timeZone': 'Asia/Kolkata'},
        # 'attendees': [{'email': candidate_email}],
        'conferenceData': {
            'createRequest': {
                'requestId': 'sample123',
                'conferenceSolutionKey': {'type': 'hangoutsMeet'}
            }
        }
    }
    event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()
    return event['conferenceData']['entryPoints'][0]['uri']

class RecruiterState(BaseModel):
    job_description: str
    summary: str = None
    questions: list[str] = []
    question_index: int = 0
    # answer: str = None
    answer: Optional[str] = None
    current_question: str = None
    transcript: list = []
    response: str = None
