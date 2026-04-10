import matplotlib
matplotlib.use('Agg') # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from utils.database_manager import DatabaseManager
import pandas as pd

class AnalyticsEngine:
    def __init__(self):
        self.db = DatabaseManager()

    def generate_charts(self):
        df = self.db.get_data_pandas()
        
        if df.empty:
            return None, None

        sns.set_theme(style="darkgrid")
        
        # 1. Pie Chart - Emotion Distribution
        emotion_counts = df['emotion'].value_counts()
        
        fig1, ax1 = plt.subplots(figsize=(6, 6))
        ax1.pie(emotion_counts, labels=emotion_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("pastel"))
        ax1.axis('equal')
        plt.title('Emotion Distribution')
        
        buf1 = io.BytesIO()
        plt.savefig(buf1, format='png', transparent=True)
        plt.close(fig1)
        pie_b64 = base64.b64encode(buf1.getvalue()).decode('utf-8')

        # 2. Line Chart - Emotion over Time
        # Convert timestamp to proper datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Just creating a simple frequency plot over time would be best, 
        # or categorical plot
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        sns.scatterplot(x='timestamp', y='emotion', data=df, ax=ax2, hue='emotion', palette="deep", s=100)
        plt.title('Emotion Timeline')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        buf2 = io.BytesIO()
        plt.savefig(buf2, format='png', transparent=True)
        plt.close(fig2)
        line_b64 = base64.b64encode(buf2.getvalue()).decode('utf-8')

        return f"data:image/png;base64,{pie_b64}", f"data:image/png;base64,{line_b64}"
