from flask import Flask, send_from_directory,  abort
import os
import signal
import sys

# Initialize the Flask app
app = Flask(__name__)

# Base paths for static files
IMAGE_PATH = "../suno-ai-music-prompts/image"
AUDIO_PATH = "../suno-ai-music-prompts/audio"

# Serve images from the image folder
@app.route('/images/<filename>')
def serve_image(filename):
    try:
        return send_from_directory(IMAGE_PATH, filename)
    except FileNotFoundError:
        abort(404)

# Serve audio files from the audio folder
@app.route('/audio/<filename>')
def serve_audio(filename):
    try:
        return send_from_directory(AUDIO_PATH, filename)
    except FileNotFoundError:
        abort(404)

# List all images
@app.route('/list/images')
def list_images():
    try:
        files = os.listdir(IMAGE_PATH)
        return {"images": files}
    except FileNotFoundError:
        return {"error": "Image directory not found"}, 404

# List all audio files
@app.route('/list/audio')
def list_audio():
    try:
        files = os.listdir(AUDIO_PATH)
        return {"audio": files}
    except FileNotFoundError:
        return {"error": "Audio directory not found"}, 404


# Signal handler to handle termination gracefully
def handle_sigterm(*args):
    print("Flask server is shutting down...")
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGTERM, handle_sigterm)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
