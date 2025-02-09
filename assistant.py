import ctypes
import subprocess
import threading
import time
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import pyautogui
import requests
import speech_recognition as sr
from tqdm import tk
from weather import Weather
from camera import Camera
from object_detection import ObjectDetection
from assistant_gui import AssistantGUI


class FridayAssistant:
    def __init__(self):
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)  # Select voice
        self.engine.setProperty('rate', 150)  # Set speech speed (words per minute)
        self.engine.setProperty('volume', 1)  # Set volume (0.0 to 1.0)

        self.weather = Weather(self.engine)  # Weather service
        self.camera = Camera(self.engine)  # Camera service
        self.object_detection = ObjectDetection(self.engine)  # Object detection service
        self.gui = AssistantGUI(self)  # GUI
        self.recognizer = sr.Recognizer()  # Speech recognition
        self.app_paths = {
            "camera": "path_to_camera_app",  # Replace with actual path
            "google chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",  # Example path for Chrome
        }

    def talk(self, text, language='en'):
        """Speaks the given text with language support and customization."""
        self.engine.setProperty('voice', self.get_voice_for_language(language))  # Update voice for language
        self.engine.say(text)
        self.engine.runAndWait()
        print(f"Assistant says: {text}")
        self.gui.update_output(text)  # Update the GUI output area
        time.sleep(1)

    def get_voice_for_language(self, language):
        """Gets the appropriate voice for the given language."""
        voices = self.engine.getProperty('voices')
        if language == 'en':
            return voices[1].id  # English voice
        elif language == 'es':
            return voices[2].id  # Spanish voice (if available)
        else:
            return voices[1].id  # Default to English if language is unknown

    def take_command(self):
        """Listens for a voice command and returns it."""
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
            try:
                command = self.recognizer.recognize_google(audio, language='en-in')
                print("You said: " + command)
                return command.lower(), True
            except Exception as e:
                print("Say that again please...")
                return "None", False

    def text_input(self):
        """Text-based input method for non-voice environments."""
        print("Please enter your command:")
        command = input().lower()
        return command, True

    def process_command(self, command, input_type='voice'):
        """Processes the command based on voice or text input."""
        print(f"Processing command: {command}")

        # Handle different commands more naturally
        if 'play' in command:
            song = command.replace('play', '').strip()
            self.talk(f"Playing {song}")
            pywhatkit.playonyt(song)
        elif 'open' in command or 'go to' in command or 'locate' in command:
            command = command.replace('open', '').replace('go to', '').strip()
            pyautogui.press('super')
            pyautogui.typewrite(command)
            pyautogui.sleep(1)
            pyautogui.press('enter')
            self.talk(f"Opening {command}...")
        elif 'time' in command:
            current_time = datetime.datetime.now().strftime('%I:%M %p')
            self.talk(f"The current time is {current_time}")
        elif 'who is' in command:
            person = command.replace('who is', '').strip()
            info = wikipedia.summary(person, 1)
            self.talk(info)
        elif 'calculate' in command:
            expression = command.replace('calculate', '').strip()
            try:
                result = eval(expression)
                self.talk(f"The result is {result}")
            except Exception as e:
                self.talk("There was an error in calculation.")
        elif "sleep" in command:
            self.talk("Going to sleep...")
            subprocess.call("shutdown / h")
        elif 'lock window' in command:
            self.talk("Locking the screen now.")
            ctypes.windll.user32.LockWorkStation()
        elif 'joke' in command:
            joke = pyjokes.get_joke()
            self.talk(joke)
        elif 'weather' in command:
            city = command.replace('weather', '').strip()
            self.weather.get_weather(city)
            self.talk(self.weather.get_weather(city))
            print(f"Weather in {city}")
        elif 'cheese' in command or 'chees' in command:
            self.camera.capture_image()
            self.talk("Capturing image now.")
            print("Capturing image.")
        elif 'detect' in command:
            self.object_detection.detect_objects()
            self.talk("Detecting objects.")
            print("Detecting objects.")
        elif 'exit' in command:
            self.talk('Thanks for your time.')
            self.gui.window.quit()

    def handle_input(self, input_type='voice'):
        """Handles either voice or text input."""
        if input_type == 'voice':
            threading.Thread(target=self.voice_input_thread).start()
        else:
            threading.Thread(target=self.text_input_thread).start()

    def voice_input_thread(self):
        """Threaded voice input handling."""
        command, valid = self.take_command()
        if valid:
            self.process_command(command, 'voice')

    def text_input_thread(self):
        """Threaded text input handling."""
        command, valid = self.text_input()
        if valid:
            self.process_command(command, 'text')

    def run(self):
        """Run the assistant's main loop."""
        self.gui.run()


if __name__ == "__main__":
    assistant = FridayAssistant()
    assistant.run()
