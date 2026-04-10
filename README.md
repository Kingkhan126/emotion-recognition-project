# emotion-recognition-project
# Smart Real-Time Emotion Recognition System with Intelligent Feedback

This project is an AI-based web application that detects human emotions in real-time using a webcam. It provides an intelligent feedback mechanism, voice responses, and tracks emotion analytics.

## Features
- **Real-Time Emotion Detection**: Analyzes video frames from your webcam to classify your current emotion into 7 categories (Happy, Sad, Angry, Surprise, Fear, Disgust, Neutral).
- **Voice Feedback Engine**: Leverages `pyttsx3` to asynchronously speak comforting or appropriate phrases based on your prominent emotion.
- **Emotion Tracking Analytics**: Logs all detections to a local SQLite database and generates detailed pie/line charts of emotion distributions.
- **Smart Alerts**: Warns you if you have been feeling "Sad" for an extended period, advising you to take a break or talk to someone.
- **Premium UI Dashboard**: A glassmorphic dark-theme user interface for easy tracking and monitoring.

## Folder Structure
```
d:\project
│   requirements.txt
│   README.md
├── backend
│   ├── app.py                      # Main Flask Server API
│   ├── create_placeholder_model.py # Helper script to create an empty CNN
│   ├── train_model.py              # Script to train CNN with FER-2013 data
│   └── utils/
│       ├── emotion_detector.py     # Image proc & TF model invoker
│       ├── database_manager.py     # SQLite and Pandas
│       ├── voice_engine.py         # Pyttsx3 TTS thread
│       └── analytics.py            # Matplotlib charts engine
├── frontend
│   ├── index.html                  # UI Dashboard
│   ├── style.css                   # Glassmorphic Styles
│   └── script.js                   # Webcam & API integrations
├── database                        # Generated after run
│   └── emotions.db                 
└── model                           # Generated after run
    └── emotion_model.hdf5          
```

## Setup & Run Instructions

**Step 1: Install Dependencies**
Ensure you have Python 3.8+ installed. From the `d:\project` directory, run:
```bash
pip install -r requirements.txt
```

**Step 2: Generate the Model Structure**
Because training the CNN from scratch takes a long time, use the following script to generate a placeholder model with randomized weights so the application works correctly out-of-the-box (it will predict random emotions until you actually train it).
```bash
python backend/create_placeholder_model.py
```
*(Optional) If you have the `FER-2013` dataset, place it in `backend/data/train` and `backend/data/test`, and run `python backend/train_model.py` to train your custom model.*

**Step 3: Run the Web Application**
Start the main server:
```bash
python backend/app.py
```
The server will start on `http://127.0.0.1:5000`.

**Step 4: Use the Application**
1. Open your web browser and go to `http://localhost:5000`.
2. Click **Start Camera** and grant your browser permission to use your webcam.
3. Allow a moment for the application to detect faces. It will display the box and emotion, update the SQLite database, and speak out via Voice Feedback.
