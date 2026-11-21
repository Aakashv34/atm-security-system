from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")  # pretrained model, downloads automatically

cap = cv2.VideoCapture(0)  # 0 = webcam

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, verbose=False)
    annotated = results[0].plot()

    cv2.imshow("ATM Security", annotated)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()