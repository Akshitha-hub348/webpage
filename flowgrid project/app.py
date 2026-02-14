from flask import Flask, render_template, jsonify, request, Response
import threading
import time
import cv2
from sirendetector import detect_siren
from flask import jsonify
import random

from detector import detect_vehicles
from signal_logic import TrafficSignalSystem

app = Flask(__name__)

signal_system = TrafficSignalSystem()

# Choose input source:
# VIDEO_SOURCE = 0   # webcam
VIDEO_SOURCE = "traffic.mp4"   # video file

cap = cv2.VideoCapture(VIDEO_SOURCE)

latest_frame = None


def ai_vehicle_detection_loop():
    global latest_frame

    while True:
        ret, frame = cap.read()

        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # Resize for speed
        frame = cv2.resize(frame, (900, 500))

        vehicle_count, boxes = detect_vehicles(frame)

        # Draw boxes
        for (x1, y1, x2, y2) in boxes:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        cv2.putText(frame, f"Vehicles: {vehicle_count}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        # For prototype: treat this as Lane A feed
        counts = {
            "Lane A": vehicle_count,
            "Lane B": int(vehicle_count * 0.6),
            "Lane C": int(vehicle_count * 0.4),
            "Lane D": int(vehicle_count * 0.8)
        }

        signal_system.update_vehicle_counts(counts)

        latest_frame = frame

        time.sleep(1)


def signal_loop():
    while True:
        signal_system.update()
        time.sleep(1)


def generate_frames():
    global latest_frame

    while True:
        if latest_frame is None:
            continue

        ret, buffer = cv2.imencode(".jpg", latest_frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/status")
def status():
    return jsonify(signal_system.get_status())


@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/ambulance", methods=["POST"])
def ambulance():
    data = request.json
    lane = data.get("lane")

    if lane:
        signal_system.set_ambulance_priority(lane)
        return jsonify({"message": f"🚑 Green corridor activated for {lane}!"})

    return jsonify({"error": "Lane not provided"}), 400

@app.route("/gps")
def gps():
    # Demo GPS (random movement simulation)
    lat = 17.3850 + random.uniform(-0.01, 0.01)
    lon = 78.4867 + random.uniform(-0.01, 0.01)

    return jsonify({"lat": lat, "lon": lon})



@app.route("/clear_ambulance", methods=["POST"])
def clear_ambulance():
    signal_system.clear_ambulance_priority()
    return jsonify({"message": "✅ Ambulance mode cleared. Normal traffic resumed."})

def siren_callback():
    print("🚑 Ambulance Siren Detected - Activating Green Corridor for Lane A")
    signal_system.set_ambulance_priority("Lane A")


if __name__ == "__main__":
    threading.Thread(target=ai_vehicle_detection_loop, daemon=True).start()
    threading.Thread(target=signal_loop, daemon=True).start()
    threading.Thread(target=detect_siren, args=(siren_callback,), daemon=True).start()
    print("Starting siren detection thread...")
    app.run(debug=True)


