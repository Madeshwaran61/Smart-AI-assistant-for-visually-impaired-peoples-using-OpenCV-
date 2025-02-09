import cv2
import numpy as np
import pyttsx3
import queue
import threading

class ObjectDetection:
    def __init__(self, engine, assistant=None):
        self.engine = engine
        self.assistant = assistant  # Link to the assistant
        self.net = cv2.dnn.readNetFromDarknet('yolov4.cfg', 'yolov4.weights')
        with open('coco.names', 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]

        # Queue for managing speech synthesis
        self.speech_queue = queue.Queue()
        self.speech_thread = threading.Thread(target=self.process_speech_queue, daemon=True)
        self.speech_thread.start()

        # Personal object database
        self.personal_objects = {}

    def process_speech_queue(self):
        """Threaded speech processor to handle speech synthesis without blocking."""
        while True:
            text = self.speech_queue.get()
            self.engine.say(text)
            self.engine.runAndWait()
            self.speech_queue.task_done()

    def speak(self, text):
        """Add text to the speech queue."""
        self.speech_queue.put(text)

    def add_personal_object(self, object_name, description):
        """Add personal objects to the database."""
        self.personal_objects[object_name.lower()] = description

    def detect_objects(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            blob = cv2.dnn.blobFromImage(frame, 1 / 255, (416, 416), swapRB=True, crop=False)
            self.net.setInput(blob)
            layer_names = self.net.getLayerNames()
            output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
            outputs = self.net.forward(output_layers)

            boxes = []
            confidences = []
            class_ids = []
            detected_objects = []  # For scene understanding

            for output in outputs:
                for detection in output:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5:
                        center_x = int(detection[0] * frame.shape[1])
                        center_y = int(detection[1] * frame.shape[0])
                        width = int(detection[2] * frame.shape[1])
                        height = int(detection[3] * frame.shape[0])
                        x = int(center_x - width / 2)
                        y = int(center_y - height / 2)

                        boxes.append([x, y, width, height])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
            if len(indices) > 0:
                for i in indices.flatten():
                    x, y, w, h = boxes[i]
                    label = self.classes[class_ids[i]]
                    color_name = self.get_color_name(frame, x, y, w, h)
                    position = self.get_relative_position(x + w // 2, frame.shape[1])
                    distance = self.calculate_distance(w)

                    description = f"{label} of color {color_name} is {position}, approximately {distance:.2f} cm away."
                    detected_objects.append(description)
                    self.speak(description)

                    # Personal object recognition
                    if label.lower() in self.personal_objects:
                        personal_description = f"{self.personal_objects[label.lower()]} is detected."
                        self.speak(personal_description)

                    # Draw bounding boxes
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    cv2.putText(frame, description, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            # Scene understanding
            if detected_objects:
                scene_description = "The scene contains: " + ", ".join(detected_objects)
                self.speak(scene_description)

            # Display frame
            cv2.imshow('Enhanced Object Detection', frame)

            if cv2.waitKey(1) == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def calculate_distance(self, width_in_pixels):
        """Calculate distance based on bounding box width."""
        focal_length = 600  # Example focal length (in pixels)
        real_width = 15  # Example real width of the object (in cm)
        distance = (real_width * focal_length) / width_in_pixels
        return distance

    def get_relative_position(self, center_x, frame_width):
        """Determine the relative position of an object in the frame."""
        if center_x < frame_width * 0.33:
            return "to your left"
        elif center_x > frame_width * 0.66:
            return "to your right"
        else:
            return "in front of you"

    def get_color_name(self, frame, x, y, w, h):
        """Get the dominant color name of an object."""
        cropped = frame[y:y + h, x:x + w]
        average_color = np.mean(cropped, axis=(0, 1))  # Average BGR color
        color_name = self.map_color(average_color)
        return color_name

    def map_color(self, bgr):
        """Map BGR color to a color name."""
        blue, green, red = bgr
        if red > 150 and green < 100 and blue < 100:
            return "red"
        elif green > 150 and red < 100 and blue < 100:
            return "green"
        elif blue > 150 and red < 100 and green < 100:
            return "blue"
        else:
            return "unknown color"


if __name__ == "__main__":
    engine = pyttsx3.init()
    object_detection = ObjectDetection(engine)

    # Add personal objects
    object_detection.add_personal_object("backpack", "your black backpack")
    object_detection.add_personal_object("wallet", "your leather wallet")

    object_detection.detect_objects()
