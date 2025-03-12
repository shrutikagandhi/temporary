from flask import Flask, render_template, jsonify, send_from_directory
import requests
import speech_recognition as sr
from pydub import AudioSegment
import os

app = Flask(__name__, static_folder='.', template_folder='.')

BASE_URL = "https://bizonet.azurewebsites.net/api/erp_bizonet_demo/raw-audio-blobs"

def fetch_audio_files():
    """Fetch the list of audio files from the base URL."""
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        audio_data = response.json()
        audio_files = [item['audio_file_url'] for item in audio_data if 'audio_file_url' in item]
        return audio_files
    return []

def convert_webm_to_wav(webm_url):
    """Download and convert a WebM audio file to WAV format."""
    webm_file_path = "temp_audio.webm"
    wav_file_path = "temp_audio.wav"
    
    response = requests.get(webm_url, stream=True)
    if response.status_code == 200:
        with open(webm_file_path, "wb") as webm_file:
            webm_file.write(response.content)
        
        # Convert webm to wav
        audio = AudioSegment.from_file(webm_file_path, format="webm")
        audio.export(wav_file_path, format="wav")
        
        os.remove(webm_file_path)  # Clean up
        return wav_file_path
    return None

def convert_audio_to_text(audio_url):
    """Convert an audio file to text using Google Speech Recognition."""
    recognizer = sr.Recognizer()
    wav_file_path = convert_webm_to_wav(audio_url)
    if not wav_file_path:
        return "Error: Audio conversion failed."
    
    try:
        with sr.AudioFile(wav_file_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            os.remove(wav_file_path)  # Clean up
            return text
    except Exception as e:
        return f"Error: {e}"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/get-text')
def get_text():
    audio_files = fetch_audio_files()
    if len(audio_files) < 2:
        return jsonify({"text": "Not enough audio files found."})
    
    audio_url = audio_files[1]  # Skip the first link and read the second
    text = convert_audio_to_text(audio_url)
    return jsonify({"text": text})

@app.route('/style.css')
def serve_css():
    return send_from_directory('.', 'style.css')

@app.route('/script.js')
def serve_js():
    return send_from_directory('.', 'script.js')

if __name__ == "__main__":
    app.run(debug=True)