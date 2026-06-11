import os
import cv2
import time
import sqlite3
import numpy as np
from datetime import datetime

from config import DETECTION_INTERVAL, ALERT_COOLDOWN_SECONDS
from utils.email_alert import send_email_alert
from utils.rules import RuleEngine
from utils.context_rules import allowed_alert_for_location

DB_PATH      = os.environ.get("DB_PATH",      "/tmp/vigilix.db")
EVIDENCE_DIR = os.environ.get("EVIDENCE_DIR", "evidence")

last_alert   = {}
rule_engine  = RuleEngine()


def parse_source(source):
    source = str(source).strip()
    return int(source) if source.isdigit() else source


def save_alert(camera, detection, frame):
    label      = detection["label"]
    risk       = detection["risk"]
    confidence = detection["confidence"]

    if risk == "Low":
        return
    if not allowed_alert_for_location(camera["location_type"], label):
        return

    key = f"{camera['id']}_{label}_{risk}"
    now = time.time()
    if key in last_alert and now - last_alert[key] < ALERT_COOLDOWN_SECONDS:
        return
    last_alert[key] = now

    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    safe_label = label.replace(" ", "_").replace("/", "_")
    filename   = f"cam_{camera['id']}_{safe_label}_{int(now)}.jpg"
    path       = os.path.join(EVIDENCE_DIR, filename)
    cv2.imwrite(path, frame)

    dt         = datetime.now()
    created    = dt.strftime("%Y-%m-%d %H:%M:%S")
    alert_date = dt.strftime("%Y-%m-%d")
    alert_day  = dt.strftime("%A")
    alert_time = dt.strftime("%I:%M:%S %p")

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        INSERT INTO alerts (user_id, camera_id, threat_type, risk_level, confidence,
                            evidence_path, alert_date, alert_day, alert_time, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (camera["user_id"], camera["id"], label, risk,
         str(round(float(confidence), 2)), filename,
         alert_date, alert_day, alert_time, created)
    )
    conn.commit()
    conn.close()

    body = f"""Safety Alert

Camera: {camera['camera_name']}
Location: {camera['location']}
Location Type: {camera['location_type']}
Alert: {label}
Risk Level: {risk}
Date: {alert_date}
Day: {alert_day}
Time: {alert_time}

Evidence screenshot is attached.
"""
    send_email_alert(camera["alert_email"], f"Safety Alert - {label}", body, path)


def draw_box(frame, detection):
    x1, y1, x2, y2 = map(int, detection["box"])
    label = detection["label"]
    risk  = detection["risk"]
    conf  = detection["confidence"]
    color = (0, 255, 0)
    if risk == "High":
        color = (0, 0, 255)
    elif risk == "Medium":
        color = (0, 200, 255)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    text = f"{label} {conf:.2f}"
    cv2.rectangle(frame, (x1, max(y1 - 30, 0)), (min(x1 + len(text) * 10, frame.shape[1]), y1), color, -1)
    cv2.putText(frame, text, (x1 + 4, max(y1 - 9, 16)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)


def error_frame(message):
    frame = np.zeros((420, 720, 3), dtype=np.uint8)
    frame[:] = (15, 23, 42)
    cv2.putText(frame, message, (70, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    cv2.putText(frame, "Use an RTSP URL or webcam index", (90, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
    return frame


def generate_frames(camera, detector):
    source = parse_source(camera["source"])
    cap    = cv2.VideoCapture(source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
    cap.set(cv2.CAP_PROP_FPS,          15)
    cap.set(cv2.CAP_PROP_BUFFERSIZE,   1)

    if not cap.isOpened():
        frame = error_frame("Camera not reachable")
        _, buffer = cv2.imencode(".jpg", frame)
        while True:
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
            time.sleep(1)

    frame_index        = 0
    latest_detections  = []

    while True:
        ok, frame = cap.read()
        if not ok:
            if isinstance(source, str) and not str(source).lower().startswith("rtsp"):
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            cap.release()
            time.sleep(1)
            cap = cv2.VideoCapture(source)
            continue

        frame       = cv2.resize(frame, (720, 420))
        frame_index += 1

        if frame_index % DETECTION_INTERVAL == 0:
            latest_detections  = detector.detect(frame)
            latest_detections += rule_engine.extra_events(latest_detections)

        alert_present = False
        for det in latest_detections:
            if allowed_alert_for_location(camera["location_type"], det["label"]):
                draw_box(frame, det)
                if det["risk"] in ["High", "Medium"]:
                    save_alert(camera, det, frame)
                    alert_present = True

        cv2.rectangle(frame, (0, 0), (720, 62), (0, 0, 0), -1)
        cv2.putText(frame, f"{camera['camera_name']} | {camera['location']} | {camera['location_type']}",
                    (14, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2)
        cv2.putText(frame, f"Live Safety Monitoring | Events: {len(latest_detections)}",
                    (14, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1)
        if alert_present:
            cv2.rectangle(frame, (0, 365), (720, 420), (0, 0, 150), -1)
            cv2.putText(frame, "ALERT DETECTED - EVIDENCE SAVED",
                        (16, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2)

        ret, buffer = cv2.imencode(".jpg", frame)
        if ret:
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
