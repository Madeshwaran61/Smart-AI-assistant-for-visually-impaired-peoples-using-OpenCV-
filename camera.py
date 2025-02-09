import cv2
from PIL import Image, ImageTk

class Camera:
    def __init__(self, engine):
        self.engine = engine

    def capture_image(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Unable to open camera.")
            return

        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to capture frame.")
            cap.release()
            return

        cv2.imwrite("image.jpg", frame)
        cap.release()

        img = Image.open("image.jpg")
        img = img.resize((250, 250), Image.Resampling.LANCZOS)  # Updated line
        img = ImageTk.PhotoImage(img)
        self.engine.say("Image captured successfully.")
