import cv2
import os
import time
import datetime
import numpy as np
from flask import Flask, render_template, Response, request

app = Flask(__name__)

# Function to ensure that a directory exists, and if not, create it
def ensure_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def record_video(cap, fps, resolution, video_dir):
    ensure_directory(video_dir)  # Ensure that the directory exists

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(video_dir, f"recorded_video_{timestamp}.mp4")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, resolution)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Write frame to video
        out.write(frame)

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    out.release()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    cap = cv2.VideoCapture(0)
    fps = 30  # You can adjust this based on your webcam's capabilities
    resolution = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    return Response(record_video(cap, fps, resolution, 'recorded_videos'), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
