
import os
import json
import streamlit as st
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2 import service_account
load_dotenv()
# Define your service account file and scopes
# SERVICE_ACCOUNT_FILE = 'service_account.json'  # Path to your service account JSON
SCOPES = ['https://www.googleapis.com/auth/presentations', 'https://www.googleapis.com/auth/drive']
service_account_info = json.loads(os.getenv("JSON_DATA"))
credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
# Authenticate and initialize the Google Slides and Drive API clients
# credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
slides_service = build('slides', 'v1', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)

# Function to create a new presentation
def create_presentation(title):
    presentation = slides_service.presentations().create(body={"title": title}).execute()
    st.write(f"Created presentation with ID: {presentation['presentationId']}")
    return presentation['presentationId']

# Function to add text to title and subtitle placeholders
def add_text_to_title_and_subtitle(presentation_id, title_text, subtitle_text):
    presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
    first_slide = presentation['slides'][0]

    title_placeholder_id = None
    subtitle_placeholder_id = None

    for element in first_slide['pageElements']:
        if 'shape' in element and 'placeholder' in element['shape']:
            placeholder_type = element['shape']['placeholder']['type']
            if placeholder_type in ['TITLE', 'CENTERED_TITLE']:
                title_placeholder_id = element['objectId']
            elif placeholder_type == 'SUBTITLE':
                subtitle_placeholder_id = element['objectId']

    requests = []
    if title_placeholder_id:
        requests.append({
            'insertText': {
                'objectId': title_placeholder_id,
                'insertionIndex': 0,
                'text': title_text
            }
        })
    if subtitle_placeholder_id:
        requests.append({
            'insertText': {
                'objectId': subtitle_placeholder_id,
                'insertionIndex': 0,
                'text': subtitle_text
            }
        })

    if requests:
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
        st.write(f"Added text to title: {title_text} and subtitle: {subtitle_text}")

# Function to share the presentation
def share_presentation(presentation_id, email):
    permission = {
        'type': 'user',
        'role': 'reader',
        'emailAddress': email
    }
    drive_service.permissions().create(
        fileId=presentation_id,
        body=permission,
        fields='id'
    ).execute()
    st.write(f"Shared the presentation with {email}")

# Streamlit interface
st.title("Google Slides Presentation Creator")

# Input fields
presentation_title = st.text_input("Presentation Title", value="Hello")
title_text = st.text_input("Slide Title Text", value="Hello World")
subtitle_text = st.text_input("Slide Subtitle Text", value="How are you? I am fine.")
email = st.text_input("Share with Email", value="fetamasr@gmail.com")

# Create and share presentation on button click
if st.button("Create and Share Presentation"):
    presentation_id = create_presentation(presentation_title)
    add_text_to_title_and_subtitle(presentation_id, title_text, subtitle_text)
    share_presentation(presentation_id, email)
    st.success("Presentation created and shared successfully!")
