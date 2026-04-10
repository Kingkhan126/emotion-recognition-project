import cv2
import numpy as np
import os
from tensorflow.keras.models import load_model
from collections import deque
from statistics import mode

class EmotionDetector:
    def __init__(self):
        self.emotion_classes = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']
        # Load the model
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model', 'emotion_model.hdf5')
        self.history = deque(maxlen=5) # Store last 5 predictions
        
        try:
            self.model = load_model(model_path)
            self.model_loaded = True
        except Exception as e:
            print(f"Warning: Could not load emotion model: {e}")
            self.model_loaded = False
            
        # Initialize Haar Cascade for face detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def process_frame(self, frame):
        """
        Process a BGR frame from OpenCV, detect faces, and predict emotion.
        Returns a list of dicts with bounding box and emotion string.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        
        results = []
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            roi_gray = cv2.resize(roi_gray, (48, 48))
            
            emotion_label = "Model not loaded"
            
            if self.model_loaded:
                roi = roi_gray.astype('float') / 255.0
                roi = np.expand_dims(roi, axis=0)
                roi = np.expand_dims(roi, axis=-1)
                
                prediction = self.model.predict(roi)
                max_index = int(np.argmax(prediction))
                emotion_label = self.emotion_classes[max_index]
            
            results.append({
                "box": [int(x), int(y), int(w), int(h)],
                "emotion": emotion_label,
                "raw_emotion": emotion_label,
                "area": int(w * h)
            })
            
        if results:
            # Sort to find main face
            results.sort(key=lambda r: r['area'], reverse=True)
            main_face = results[0]
            
            if main_face["raw_emotion"] != "Model not loaded":
                self.history.append(main_face["raw_emotion"])
                
                # Apply majority vote (smoothing)
                try:
                    smoothed_emotion = mode(self.history)
                except:
                    # In case of tie, just pick the latest
                    smoothed_emotion = self.history[-1]
                    
                main_face["emotion"] = smoothed_emotion

        return results
