import os
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import re

load_dotenv('../.env')
google_api_key = os.getenv('GOOGLE_API_KEY')

genai.configure(api_key=google_api_key)

system_prompt = """ You are a Youtube Video Summarizer ,you accept the transcript as text and  summarizing  entire  ,providing important summary in points within 200 words
The Generated Summary from transcript will be appended here :  """


def generateYoutubeVideoSummary(transcriptTxt, system_prompt):
    model = genai.GenerativeModel("gemini-3.8-flash")
    response = model.generate_content(system_prompt+transcriptTxt)
    return response.text


def get_video_id(url):
    pattern = r'(?:v=|\/shorts\/|\/embed\/|\/youtu\.be\/|\/v\/|^)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

# method to get transcript
# from youtube video url has to be public


def extract_transcript_from_youtube_video(youtubeVideoURL):
    try:
        videoId = get_video_id(youtubeVideoURL)
        if videoId:
            print(f'video ID:::{videoId}')
        else:
            st.error('Invalid Video URL')

        api = YouTubeTranscriptApi()
        transcriptText = api.fetch(
            videoId,
            languages=['en', 'ar'],
            preserve_formatting=True
        )
        transcript = ""

        for i in transcriptText:
            # transcript += " "+i['text']
            transcript += " "+i.text
        return transcript

    except Exception as e:
        raise e


st.title('Youtube Transcript Concise Summarization ')
youtube_videoLink = st.text_input("Enter Youtube Link:")

if youtube_videoLink:

    videoId = get_video_id(youtube_videoLink)
    # print(f'video ID:::{videoId}')
    st.image(
        f"http://img.youtube.com/vi/{videoId}/0.jpg", width='stretch')
if youtube_videoLink and st.button(f"Get Summary from Video link "):
    with st.spinner('Fetching Video Summary....'):
        try:
            transcript_text = extract_transcript_from_youtube_video(
                youtube_videoLink)
            # print(transcript_text)
            if transcript_text:
                summary = generateYoutubeVideoSummary(
                    transcript_text, system_prompt)
                languages = ['en', 'ar'],
                # print(summary)
                st.markdown("## Concise Summary of youtube video")
                st.write(summary)
        except Exception as e:
            st.error(f"Problem getting Transcript: {str(e)}")


def get_video_id(url):
    pattern = r'(?:v=|\/shorts\/|\/embed\/|\/youtu\.be\/|\/v\/|^)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None
