from ultralytics import YOLO
import cv2, sys

model = YOLO("atm_best.pt")
img = cv2.imread("download.jpg")
results = model(img, imgsz=416, conf=0.4)[0]
print([(model.names[int(b.cls)], round(float(b.conf), 2)) for b in results.boxes])
cv2.imshow("Result", results.plot())
cv2.waitKey(0)