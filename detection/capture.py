import cv2, os, time

for d in ("helmet", "mask", "face"):
    os.makedirs(f"my_data/{d}", exist_ok=True)

cap = cv2.VideoCapture(0)
mode, auto, last = "face", False, 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    clean = frame.copy()
    cv2.putText(frame, f"{mode} | auto={auto} | 1=helmet 2=mask 3=face s=auto q=quit",
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.imshow("capture", frame)

    if auto and time.time() - last > 0.5:
        last = time.time()
        cv2.imwrite(f"my_data/{mode}/{int(time.time()*1000)}.jpg", clean)

    k = cv2.waitKey(1) & 0xFF
    if k == ord("1"): mode = "helmet"
    elif k == ord("2"): mode = "mask"
    elif k == ord("3"): mode = "face"
    elif k == ord("s"): auto = not auto
    elif k == ord("q"): break

cap.release()
cv2.destroyAllWindows()