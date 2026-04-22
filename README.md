# 🚦 SmartSignal India

An AI-powered adaptive traffic light automation system built for Indian road conditions.
Combines real-time traffic simulation, computer vision, and automated emergency response
into a single integrated pipeline.

---

## 🧠 Project Overview

SmartSignal India is a Python-based intelligent traffic management system that addresses
four core problems with traditional fixed-timer traffic signals:

1. **Adaptive Signal Timing** — Green light durations scale dynamically based on real-time vehicle density
2. **Emergency Vehicle Priority** — Ambulances and fire trucks automatically get a clear path
3. **Violation Detection** — Vehicles stopping on zebra crossings are flagged in real time
4. **Accident Detection & Alerts** — Stopped/crashed vehicles are detected and emergency services are notified via email

---

## 🏗️ Architecture
SmartSignal/
├── network/               # SUMO road network config files
├── simulation/            # SUMO simulation setup and vehicle routes
├── controller/
│   ├── signal_controller.py      # Adaptive signal + emergency override logic
│   ├── violation_detector.py     # YOLOv8 zebra crossing violation detection
│   └── accident_detector.py      # YOLOv8 accident detection + email alerts
└── main.py                # Entry point — runs full simulation with adaptive control

---

## ⚙️ Tech Stack

| Layer | Tool |
|---|---|
| Traffic Simulation | SUMO + traci |
| Computer Vision | YOLOv8 (Ultralytics) |
| Video Processing | OpenCV |
| Alert System | Python smtplib (Gmail) |
| Language | Python 3.14 |

---

## 🚀 Getting Started

### Prerequisites
- [SUMO Traffic Simulator](https://sumo.dlr.de/docs/Downloads.php)
- Python 3.10+
- uv (Python package manager)

### Installation

```bash
git clone https://github.com/aryan-shukl26/Smart-Signal.git
cd Smart-Signal
uv venv
.venv\Scripts\activate
uv pip install traci sumolib ultralytics opencv-python pandas
```

### Add SUMO to PATH
Add `C:\Program Files (x86)\Eclipse\Sumo\bin` to your system environment variables.

### Run the Simulation

```bash
uv run python main.py
```

---

## 📦 Module Details

### Module 1 — Adaptive Signal Timing
Reads real-time vehicle counts on all 4 incoming edges every 30 simulation steps.
Compares North/South vs East/West traffic load and dynamically sets green light
duration between 10s (minimum) and 60s (maximum) using Webster's proportional logic.

### Module 2 — Emergency Vehicle Priority
Detects emergency-type vehicles entering any incoming edge and immediately overrides
the current signal phase to green for that direction. Normal adaptive control resumes
once the vehicle clears the intersection.

### Module 3 — Violation Detection
Uses YOLOv8 to detect vehicles in each video frame. A configurable polygon defines
the zebra crossing zone. Any vehicle whose center point falls inside the zone triggers
a violation log entry with timestamp and confidence score.

### Module 4 — Accident Detection & Alerts
Tracks vehicle positions across consecutive frames using YOLOv8's built-in tracker.
If a vehicle moves less than 50px over 5 consecutive frames, it is flagged as a
potential accident. An automated email alert is dispatched via Gmail SMTP with
vehicle ID, type, timestamp, and location.

---

## 📊 Sample Output
Step 3510:
Vehicle counts: {'north': 3, 'south': 2, 'east': 5, 'west': 8}
Busiest direction: west
Green duration set to: 26s
🚨 EMERGENCY OVERRIDE: ambulance_1 on north_in → forcing north GREEN
🚨 Violation at 16.67s | Frame 200 | car | conf: 0.45
🚨 Possible accident at frame 225 (18.75s)
✅ Alert email sent for vehicle ID:13

---

## 🔭 Future Scope

- Helmet violation detection using a fine-tuned YOLO model
- Integration with TomTom / HERE Maps API for real-world traffic data
- Green wave coordination across multiple intersections
- Streamlit dashboard for live monitoring
- GPS-based emergency vehicle tracking

---

## 👤 Author

**Aryan Shukla**  
Business Analyst @ RBL Bank | B.Tech — AI & ML  
[LinkedIn](https://linkedin.com/in/shuklaryan) • [GitHub](https://github.com/aryan-shukl26)

---

## 📄 License

MIT License — free to use, modify, and distribute.
