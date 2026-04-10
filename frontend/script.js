const video = document.getElementById('videoElement');
const canvas = document.getElementById('overlay');
const ctx = canvas.getContext('2d');
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const placeholderDiv = document.getElementById('video-placeholder');
const statusDot = document.getElementById('cam-status-dot');
const statusText = document.getElementById('cam-status-text');
const dominantEmotionEl = document.getElementById('dominant-emotion');

// Analytics elements
const btnRefresh = document.getElementById('refresh-analytics');
const pieImg = document.getElementById('pie-chart');
const lineImg = document.getElementById('line-chart');
const piePh = document.getElementById('pie-placeholder');
const linePh = document.getElementById('line-placeholder');

// Alert System
const alertBox = document.getElementById('smart-alert');
const alertCloseBtn = document.getElementById('close-alert');

let isStreaming = false;
let stream = null;
let captureInterval = null;
let sadCounter = 0;
const SAD_THRESHOLD = 10; // Trigger alert after 10 consecutive sad detections

const API_BASE = 'http://localhost:5000';

startBtn.addEventListener('click', async () => {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
        video.srcObject = stream;
        isStreaming = true;
        
        startBtn.disabled = true;
        stopBtn.disabled = false;
        placeholderDiv.classList.add('hidden');
        statusDot.classList.add('active');
        statusText.textContent = "Camera On";

        // Notify backend
        await fetch(`${API_BASE}/start_camera`, { method: 'POST' });

        // Start capture loop
        // Ensure video is playing so naturalWidth/Height are available
        video.onloadeddata = () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            // 3 FPS to balance load
            captureInterval = setInterval(processFrame, 333); 
        };

    } catch (err) {
        alert("Could not access camera: " + err);
    }
});

stopBtn.addEventListener('click', async () => {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
    video.srcObject = null;
    isStreaming = false;
    clearInterval(captureInterval);
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    startBtn.disabled = false;
    stopBtn.disabled = true;
    placeholderDiv.classList.remove('hidden');
    statusDot.classList.remove('active');
    statusText.textContent = "Camera Off";
    dominantEmotionEl.textContent = "--";

    // Notify backend
    await fetch(`${API_BASE}/stop_camera`, { method: 'POST' });
});

async function processFrame() {
    if (!isStreaming) return;

    // Use a temporary canvas to get the base64 image data
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = video.videoWidth;
    tempCanvas.height = video.videoHeight;
    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);
    
    const base64Image = tempCanvas.toDataURL('image/jpeg', 0.8);

    try {
        const response = await fetch(`${API_BASE}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: base64Image })
        });
        
        if (!response.ok) return;

        const data = await response.json();
        drawBoxes(data.detections);
        updateUI(data.detections);
    } catch (e) {
        console.error("Frame processing failed", e);
    }
}

function drawBoxes(detections) {
    // Clear previous
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    if (!detections) return;

    detections.forEach(det => {
        const [x, y, w, h] = det.box;
        const emotion = det.emotion;
        
        // Settings based on emotion for visual flair
        let color = '#8b5cf6'; // default purple
        if (emotion === 'Happy') color = '#22c55e';
        else if (emotion === 'Sad') color = '#3b82f6';
        else if (emotion === 'Angry') color = '#ef4444';
        else if (emotion === 'Fear') color = '#f97316';
        
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.strokeRect(x, y, w, h);
        
        ctx.fillStyle = color;
        ctx.font = '16px Inter, sans-serif';
        ctx.fillText(emotion, x, y > 20 ? y - 10 : y + 20);
    });
}

function updateUI(detections) {
    if (!detections || detections.length === 0) return;
    
    // Pick largest face's emotion
    const largestFace = detections.reduce((prev, current) => {
        const areaPrev = prev.box[2] * prev.box[3];
        const areaCurr = current.box[2] * current.box[3];
        return (areaPrev > areaCurr) ? prev : current;
    });

    const currentEmotion = largestFace.emotion;
    dominantEmotionEl.textContent = currentEmotion;

    // Smart Alert logic
    if (currentEmotion === 'Sad') {
        sadCounter++;
        if (sadCounter >= SAD_THRESHOLD) {
            alertBox.classList.remove('hidden');
        }
    } else {
        sadCounter = Math.max(0, sadCounter - 1); // Slowly recover if not sad
    }
}

alertCloseBtn.addEventListener('click', () => {
    alertBox.classList.add('hidden');
    sadCounter = 0; // reset for a while
});

// Analytics Logic
async function fetchAnalytics() {
    try {
        const response = await fetch(`${API_BASE}/get-analytics`);
        const data = await response.json();
        
        if (data.pie_chart) {
            pieImg.src = data.pie_chart;
            pieImg.classList.remove('hidden');
            piePh.classList.add('hidden');
        } else {
            pieImg.classList.add('hidden');
            piePh.classList.remove('hidden');
        }
        
        if (data.line_chart) {
            lineImg.src = data.line_chart;
            lineImg.classList.remove('hidden');
            linePh.classList.add('hidden');
        } else {
            lineImg.classList.add('hidden');
            linePh.classList.remove('hidden');
        }
        
    } catch(e) {
        console.error("Failed to load analytics", e);
    }
}

btnRefresh.addEventListener('click', fetchAnalytics);

// Fetch initial analytics if db is not empty
fetchAnalytics();
