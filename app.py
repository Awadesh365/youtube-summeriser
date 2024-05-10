import streamlit as st
from dotenv import load_dotenv
from googletrans import Translator
from gtts import gTTS
import os

load_dotenv()  # Load all the environment variables
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

translator = Translator()

prompt = """You are YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here: """

## getting the transcript data from YouTube videos
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]

        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]

        return transcript

    except Exception as e:
        raise e


## getting the summary based on Prompt from Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text


def generate_audio(summary, language):
    tts = gTTS(text=summary, lang=language)
    tts.save("summary_audio.mp3")


st.title("YouTube Transcript Summarizer")
st.markdown("---")
youtube_link = st.text_input("Enter YouTube Video Link:")
st.markdown("---")

if youtube_link:
    video_id = youtube_link.split("=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

languages = ['English', 'French', 'German', 'Spanish', 'Italian', 'Hindi']  # Supported languages for translation
selected_language = st.selectbox("Select Language:", languages, index=0)

if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        st.markdown("## Detailed Notes:", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #3366ff;'>{summary}</p>", unsafe_allow_html=True)

        # Translate the summary to the selected language
        translated_summary = translator.translate(summary, dest=selected_language.lower()).text
        st.markdown(f"## Detailed Notes in Selected Language ({selected_language}):", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #3366ff;'>{translated_summary}</p>", unsafe_allow_html=True)

        generate_audio(translated_summary, 'en')
        audio_file = open("summary_audio.mp3", "rb")
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3")

        # Specify the file path
        file_path = f"summarized_text_{selected_language}.txt"
        try:
            # Save text output to a file
            with open(file_path, "w", encoding="utf-8") as text_file:
                text_file.write(translated_summary)
            st.success(f"Summarized text saved as {file_path}")
        except Exception as e:
            st.error(f"Error saving file: {e}")

        # Provide download button for the text file
        st.markdown("---")
        st.download_button(
            label=f"Download summarized text ({selected_language})",
            data=open(file_path, "rb").read(),
            file_name=file_path,
            mime="text/plain"
        )