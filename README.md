# ATM Security System (Prototype)

A prototype that watches an ATM camera feed and raises an alert when someone's face is covered by a **helmet** or a **mask**. Detections are stored by a Django API and shown live on a React dashboard.

> **Status: prototype.** Built for learning and portfolio purposes. Not production-ready.


## How it works

```
Camera -> YOLOv8 detection -> Django REST API -> Database + image storage -> React dashboard
```

1. The detection script reads the webcam and runs a custom YOLOv8 model on each frame.
2. If a helmet or mask is detected above the confidence threshold, it saves a snapshot and sends the alert to the API (with a 5 second cooldown to avoid duplicates).
3. Django stores the alert and image.
4. The React dashboard polls the API every 3 seconds and shows the alerts.

## Features
- Custom YOLOv8n model detecting `helmet`, `mask` and `face`
- Alert snapshots with class, time and confidence
- Dashboard with stats cards and a 7-day chart
- Filters (All, Helmet, Mask, Unreviewed)
- Mark as reviewed, delete one or many alerts
- Sound alert for new detections
- Export alerts to CSV
- **Automatic deletion of alerts and photos after 14 days** (a data-privacy measure)

## Tech stack
YOLOv8 (Ultralytics), OpenCV, Python, Django, Django REST Framework, React (Vite), SQLite

## Model and results

Trained in two stages on Google Colab (T4 GPU):

- **v1:** 1,614 images from two public Kaggle datasets (mask and helmet), converted from Pascal VOC to YOLO format and merged into 3 classes.
- **v2:** added 268 images I captured and labelled myself, because v1 failed on my webcam (it never detected a helmet and confused bare faces with masks). This is a domain gap problem: the public images looked very different from webcam footage.

| Metric | v1 | v2 |
|---|---|---|
| mAP50 | 0.863 | 0.905 |
| Precision | 0.849 | 0.873 |
| Recall | 0.811 | 0.856 |
| mAP50-95 | 0.550 | 0.607 |

Note: the v2 validation set includes my own images, so these numbers are optimistic. Real-world performance may be lower.

## How to run

Open three terminals.

**1. Backend**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install django djangorestframework django-cors-headers pillow tzdata
python manage.py migrate
python manage.py runserver
```

**2. Frontend**
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173

**3. Detection**
```bash
cd detection
python -m venv venv
venv\Scripts\activate
pip install ultralytics opencv-python requests
python run_detection.py
```
The model file is `detection/atm_best_v2.pt`. Press `q` in the camera window to quit.

To delete expired alerts manually: `python manage.py cleanup_alerts`

## Limitations
- Trained and tested mostly in one room, with mostly one person. Not tested on real ATM cameras, night footage, or many different people.
- The `face` class is the weakest, and its labels come from datasets labelled differently.
- Class imbalance: far more mask examples than helmet examples.
- Caps, hoodies, scarves and medical masks can cause false results.
- No login: anyone who can open the dashboard can view and delete alerts.
- Polling instead of WebSockets, a single camera, SQLite, and Django's development server.
- `SECRET_KEY` is in `settings.py` and must be moved to an environment variable for any real deployment.
- Privacy: a real deployment would need consent rules, secure storage and access control for face images.

## Future work
- User authentication and roles
- WebSockets for true real-time updates
- Multiple cameras and ATMs
- Email, SMS or Telegram notifications
- Larger and more varied training data, including night and low-light images
- Automated tests and Docker deployment

## Author
Aakash, MCA graduate, aspiring Python developer / data scientist