from ultralytics import YOLO
import cv2

model = YOLO("atm_best_v2.pt")
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    r = model(frame, imgsz=640, conf=0.15, verbose=False)[0]
    for b in r.boxes:
        print(model.names[int(b.cls)], round(float(b.conf), 2))
    cv2.imshow("debug", r.plot())
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()