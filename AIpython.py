import cv2
import easyocr
import socket
import time

reader = easyocr.Reader(['en', 'ar'])

def send_to_server(msg):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", 6000))
        s.sendall(msg.encode())
        s.close()
        print("[AI → SERVER]:", msg)
    except Exception as e:
        print("[ERROR sending]:", e)

cap = cv2.VideoCapture(0)

AUTHORIZED = ["2180131", "123456", "1789","-2180131","329473","-329473","733294","-733294"]

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # SHOW WEBCAM LIVE
    cv2.imshow("WEBCAM", frame)

    # OCR
    result = reader.readtext(frame, detail=0)
    raw = " ".join(result)
    print("OCR:", raw)

    # extract digits only
    clean = "".join([c for c in raw if c.isdigit()])
    print("CLEAN:", clean)

    if clean in AUTHORIZED:
        print("[ACCESS GRANTED]")
        send_to_server("OPEN")
        time.sleep(5)
    else:
        print("[ACCESS DENIED]")
        send_to_server("CLOSE")
        time.sleep(2)

    # press 'q' to close
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
