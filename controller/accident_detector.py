import cv2
import numpy as np
from ultralytics import YOLO
from collections import defaultdict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

model = YOLO("yolov8n.pt")
vehicle_history = defaultdict(list)
accident_log = []

STOPPED_THRESHOLD = 50
STOPPED_FRAMES = 5

SENDER_EMAIL = "your@gmail.com"
APP_PASSWORD = "your_app_password"
RECEIVER_EMAIL = "your@gmail.com"

def get_center(box):
    return (int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2))

def detect_accidents(frame, frame_num, fps):
    results = model.track(frame, conf=0.3, verbose=False, persist=True,
                         classes=[2, 3, 5, 7])
    annotated = frame.copy()
    accident_detected = False

    if results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.tolist()
        ids = results[0].boxes.id.tolist()
        classes = results[0].boxes.cls.tolist()

        for box, track_id, cls in zip(boxes, ids, classes):
            track_id = int(track_id)
            center = get_center(box)
            label = model.names[int(cls)]
            vehicle_history[track_id].append(center)

            if len(vehicle_history[track_id]) > STOPPED_FRAMES:
                vehicle_history[track_id].pop(0)

            if len(vehicle_history[track_id]) == STOPPED_FRAMES:
                positions = vehicle_history[track_id]
                total_movement = sum(
                    np.sqrt((positions[i][0]-positions[i-1][0])**2 +
                            (positions[i][1]-positions[i-1][1])**2)
                    for i in range(1, len(positions))
                )
                x1,y1,x2,y2 = map(int, box)
                if total_movement < STOPPED_THRESHOLD:
                    accident_detected = True
                    timestamp = round(frame_num / fps, 2)
                    accident_log.append({
                        "frame": frame_num,
                        "timestamp_sec": timestamp,
                        "vehicle_id": track_id,
                        "class": label,
                        "location": center
                    })
                    cv2.rectangle(annotated, (x1,y1), (x2,y2), (0,0,255), 2)
                    cv2.putText(annotated, f"ACCIDENT? ID:{track_id}",
                               (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
                else:
                    cv2.rectangle(annotated, (x1,y1), (x2,y2), (0,255,0), 2)
                    cv2.putText(annotated, f"{label} ID:{track_id}",
                               (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

    return annotated, accident_detected

def send_accident_alert(accident):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = "SmartSignal Alert: Possible Accident Detected"

    body = f"""
    SMARTSIGNAL INDIA - ACCIDENT ALERT
    ====================================
    Vehicle ID  : {accident["vehicle_id"]}
    Vehicle Type: {accident["class"]}
    Timestamp   : {accident["timestamp_sec"]} seconds
    Frame       : {accident["frame"]}
    Location    : {accident["location"]}

    Please dispatch emergency services to the intersection immediately.

    - SmartSignal Automated Alert System
    """

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print(f"Alert email sent for vehicle ID:{accident["vehicle_id"]}")
    except Exception as e:
        print(f"Failed to send email: {e}")
