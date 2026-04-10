import sqlite3
import pandas as pd
import datetime
import os

class DatabaseManager:
    def __init__(self):
        self.db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database')
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)
            
        self.db_path = os.path.join(self.db_dir, 'emotions.db')
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emotion_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                emotion TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def log_emotion(self, emotion):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO emotion_logs (timestamp, emotion) VALUES (?, ?)", (timestamp, emotion))
        conn.commit()
        conn.close()

    def get_history(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, emotion FROM emotion_logs ORDER BY id DESC LIMIT 100")
        rows = cursor.fetchall()
        conn.close()
        
        return [{"id": row[0], "timestamp": row[1], "emotion": row[2]} for row in rows]

    def get_data_pandas(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM emotion_logs", conn)
        conn.close()
        return df
