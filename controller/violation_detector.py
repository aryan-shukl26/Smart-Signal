import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
ZEBRA_ZONE = np.array([[50, 200], [330, 200], [330, 280], [50, 280]], np.int32)

def is_in_zone(box, zone):
    cx = int((box[0] + box[2]) / 2)
    cy = int((box[1] + box[3]) / 2)
    result = cv2.pointPolygonTest(zone, (cx, cy), False)
    return result >= 0

def detect_violations(frame):
    results = model(frame, conf=0.3, verbose=False)
    violations = []
    annotated = frame.copy()
    cv2.polylines(annotated, [ZEBRA_ZONE], True, (0, 255, 255), 2)
    cv2.putText(annotated, "Zebra Zone", (50, 195),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    for box in results[0].boxes:
        cls = int(box.cls)
        conf = float(box.conf)
        coords = box.xyxy[0].tolist()
        label = model.names[cls]
        if label in ["car", "truck", "bus", "motorcycle"]:
            if is_in_zone(coords, ZEBRA_ZONE):
                violations.append({
                    "type": "Zebra Crossing Violation",
                    "class": label,
                    "confidence": conf
                })
                color = (0, 0, 255)
                cv2.putText(annotated, "VIOLATION!",
                          (int(coords[0]), int(coords[1])-10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            else:
                color = (0, 255, 0)
            x1,y1,x2,y2 = map(int, coords)
            cv2.rectangle(annotated, (x1,y1), (x2,y2), color, 2)
            cv2.putText(annotated, f"{label} {conf:.2f}",
                       (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    return annotated, violations
