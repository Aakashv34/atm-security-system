from ultralytics import YOLO
import cv2, time, os
import requests
API_URL = "http://127.0.0.1:8000/api/alerts/"

model = YOLO("atm_best_v2.pt")
os.makedirs("snapshots", exist_ok=True)

ALERT_CLASSES = {"helmet", "mask"}
CONF = 0.5          # ignore weak detections
COOLDOWN = 5        # seconds between alerts
last_alert = 0

cap = cv2.VideoCapture(0)   # or a video file path

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, imgsz=640, conf=CONF, verbose=False)[0]
    # detected = {model.names[int(b.cls)] for b in results.boxes}
    detected = set()
    for b in results.boxes:
        n, c = model.names[int(b.cls)], float(b.conf)
        if n in ALERT_CLASSES and c > 0.6:
            detected.add(n)

    suspicious = detected & ALERT_CLASSES
    if suspicious and time.time() - last_alert > COOLDOWN:
        last_alert = time.time()
        path = f"snapshots/alert_{int(last_alert)}.jpg"
        cv2.imwrite(path, frame)
        best = max(float(b.conf) for b in results.boxes
                   if model.names[int(b.cls)] in suspicious)
        try:
            with open(path, "rb") as f:
                requests.post(API_URL,
                              data={"camera_id": "ATM-1",
                                    "label": ", ".join(suspicious),
                                    "confidence": round(best, 2)},
                              files={"snapshot": f}, timeout=3)
            print("ALERT sent:", suspicious)
        except requests.RequestException as e:
            print("Could not send alert:", e)

    cv2.imshow("ATM Security", results.plot())
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()