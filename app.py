import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import moviepy.editor as mp
import speech_recognition as sr

app = Flask(__name__)

# Directory to save uploaded files
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files["video"]
    if video_file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Save the video file
    filename = secure_filename(video_file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    video_file.save(filepath)

    # Extract audio from the video
    audio_path = extract_audio(filepath)

    # Convert audio to text
    extracted_text = convert_audio_to_text(audio_path)

    return jsonify({"text": extracted_text})

def extract_audio(video_path):
    """Extracts audio from a video file."""
    audio_path = os.path.splitext(video_path)[0] + ".wav"
    clip = mp.VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, logger=None)
    return audio_path

def convert_audio_to_text(audio_path):
    """Converts audio to text using SpeechRecognition."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Could not understand the audio"
        except sr.RequestError as e:
            return f"Error with the request: {e}"

if __name__ == "__main__":
    app.run(debug=True)
