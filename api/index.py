# Ensure you have installed the required dependencies:
# pip install openai pyttsx3 SpeechRecognition python-dotenv flask

import os
import openai
import pyttsx3
import speech_recognition as sr
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import threading

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Flask app
app = Flask(__name__)

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine_lock = threading.Lock()

def speak(text):
    """Convert text to speech."""
    with engine_lock:
        if engine._inLoop:
            engine.endLoop()
        engine.say(text)
        engine.runAndWait()

def listen():
    """Listen to user input via microphone."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
            print("Recognizing...")
            query = recognizer.recognize_google(audio)
            return query
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand that.")
            return None
        except sr.RequestError as e:
            speak(f"Error with speech recognition: {e}")
            return None

def chat_with_openai(prompt):
    """Send prompt to OpenAI and get the response."""
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # Or "gpt-4" if you have access
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except Exception as e:
        speak(f"Error with OpenAI API: {e}")
        return None

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/send', methods=['POST'])
def send():
    user_query = request.form['user_query']
    response = chat_with_openai(user_query)
    if response:
        speak(response)
    return jsonify({'assistant': response})

if __name__ == "__main__":
    app.run(debug=True)