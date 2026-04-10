from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import base64
import numpy as np
import cv2
import os

from utils.emotion_detector import EmotionDetector
from utils.database_manager import DatabaseManager
from utils.voice_engine import VoiceEngine
from utils.analytics import AnalyticsEngine

app = Flask(__name__, static_folder="../frontend", static_url_path="/")
CORS(app)

# Initialize engines
detector = EmotionDetector()
db = DatabaseManager()
voice = VoiceEngine()
analytics = AnalyticsEngine()

# State
is_camera_active = False

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/start_camera", methods=["POST"])
def start_camera():
    global is_camera_active
    is_camera_active = True
    return jsonify({"status": "Camera started", "started": True})

@app.route("/stop_camera", methods=["POST"])
def stop_camera():
    global is_camera_active
    is_camera_active = False
    return jsonify({"status": "Camera stopped", "started": False})

@app.route("/predict", methods=["POST"])
def predict():
    if not is_camera_active:
        return jsonify({"error": "Camera is stopped"}), 400
        
    data = request.json
    if 'image' not in data:
        return jsonify({"error": "No image provided"}), 400
        
    # Decode base64 image from frontend
    img_data = data['image'].split(',')[1]
    nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if frame is None:
        return jsonify({"error": "Invalid image"}), 400

    # Process frame
    results = detector.process_frame(frame)
    
    # Simple logic to find dominant emotion and log it
    # We will log the largest face's emotion
    if results:
        # Sort by bounding box area (w*h)
        largest_face = max(results, key=lambda r: r['box'][2] * r['box'][3])
        dominant_emotion = largest_face['emotion']
        
        # Log to database
        db.log_emotion(dominant_emotion)
        
        # Trigger voice feedback occasionally (handled by queue size in VoiceEngine)
        voice.speak_emotion(dominant_emotion)
    
    return jsonify({"detections": results})

@app.route("/emotion_history", methods=["GET"])
def get_history():
    history = db.get_history()
    return jsonify({"history": history})

@app.route("/get-analytics", methods=["GET"])
def get_analytics():
    pie_chart, line_chart = analytics.generate_charts()
    return jsonify({
        "pie_chart": pie_chart,
        "line_chart": line_chart
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
