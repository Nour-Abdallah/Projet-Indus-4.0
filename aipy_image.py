import cv2
import numpy as np
import easyocr
import socket
import re


# ------------------------------
#  TCP CLIENT → send OPEN/CLOSE
# ------------------------------
def send_command(cmd, host="127.0.0.1", port=6000):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send(cmd.encode())
        s.close()
        print(f"[INFO] Sent command: {cmd}")
    except Exception as e:
        print("[ERROR] Could not send command:", e)



# ------------------------------
#  OCR SETUP
# ------------------------------
reader = easyocr.Reader(['ar', 'en'], gpu=False)

# Save only NUMBER-FORMAT (no Arabic)
AUTHORIZED_PLATES = [
    "147145",
    "156956",
    "100200",
    "1312180",
    "2180131",
    "-2180131"
]


def remove_arabic(text):
    """Remove all Arabic characters, keep only English letters & numbers."""
    # Arabic unicode range: \u0600-\u06FF
    cleaned = re.sub(r'[\u0600-\u06FF]', '', text)
    # Remove spaces
    cleaned = cleaned.replace(" ", "")
    return cleaned


def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    return thresh


def extract_plate_text(plate_img):
    results = reader.readtext(plate_img, detail=0)
    text = " ".join(results)
    return text


def detect_plate(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    candidates = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        aspect = w / float(h)

        # Tunisian plate ratio
        if 2.5 < aspect < 6.5 and w > 100:
            candidates.append((x, y, w, h))

    if not candidates:
        return None, None

    x, y, w, h = sorted(candidates, key=lambda c: c[2], reverse=True)[0]
    return img[y:y+h, x:x+w], (x, y, w, h)



# ------------------------------
#  MAIN ANPR LOGIC
# ------------------------------
image_path = "132tn2180.jpg"  # test image
img = cv2.imread(image_path)

plate, box = detect_plate(img)

if plate is None:
    print("[ERROR] No plate detected!")
    send_command("CLOSE")
else:
    processed = preprocess(plate)
    raw_text = extract_plate_text(processed)

    print("\n===== RAW OCR =====")
    print(raw_text)

    # Remove Arabic, keep only numbers
    cleaned_text = remove_arabic(raw_text)

    print("\n===== CLEANED (Numbers Only) =====")
    print(cleaned_text)
    print("==================================\n")

    # Check authorization
    if cleaned_text in AUTHORIZED_PLATES:
        print("[ACCESS GRANTED]")
        send_command("OPEN")
    else:
        print("[ACCESS DENIED]")
        send_command("CLOSE")

    cv2.imshow("Plate", plate)
    cv2.imshow("Processed", processed)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
