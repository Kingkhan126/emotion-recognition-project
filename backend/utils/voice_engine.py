import pyttsx3
import threading
import queue
import time
import pythoncom

class VoiceEngine:
    def __init__(self):
        self.q = queue.Queue()
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()
        
        self.emotion_messages = {
            'Happy': "You look happy today!",
            'Sad': "You seem sad, take care. Maybe talk to someone.",
            'Angry': "You seem angry, please take a deep breath.",
            'Surprise': "You look surprised!",
            'Fear': "You look scared, are you okay?",
            'Disgust': "You seem disgusted.",
            'Neutral': "You look very calm."
        }
        self.last_spoken_emotion = None
        
    def _worker(self):
        # COM object initialization is required for background threads in Windows
        pythoncom.CoInitialize()
        
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        
        # Loop to process the queue unblocked
        while True:
            text = self.q.get()
            if text is None:
                break
            
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"Voice engine error: {e}")
            
            self.q.task_done()
            time.sleep(1)  # small buffer

    def speak_emotion(self, emotion):
        if emotion == self.last_spoken_emotion:
            return # Do not spam the same emotion linearly
            
        message = self.emotion_messages.get(emotion, f"I sense {emotion}")
        # Only allow 1 item in queue to avoid massive backlog of speech
        if self.q.empty():
            self.q.put(message)
            self.last_spoken_emotion = emotion
