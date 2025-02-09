import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import time

class AssistantGUI:
    def __init__(self, assistant):
        self.window = tk.Tk()
        self.window.title("Friday Assistant")
        self.window.geometry("800x600")
        self.window.resizable(False, False)
        self.assistant = assistant
        self.create_widgets()

    def create_widgets(self):
        canvas = tk.Canvas(self.window, width=800, height=600)
        canvas.pack(fill=tk.BOTH, expand=True)

        gradient = Image.new("RGB", (800, 600), "#000000")
        for y in range(600):
            color = (int(255 * y / 600), int(102 * y / 600), 255)
            for x in range(800):
                gradient.putpixel((x, y), color)
        gradient_photo = ImageTk.PhotoImage(gradient)
        canvas.create_image(0, 0, image=gradient_photo, anchor="nw")

        header = tk.Label(self.window, text="Friday AI Assistant", font=("Helvetica", 24, "bold"), bg="#6200ea", fg="white")
        header.place(relwidth=1, y=10)

        label = tk.Label(self.window, text="Choose your input method:", font=("Helvetica", 14), bg="#1a237e", fg="white")
        label.place(x=10, y=70)

        self.command_label = tk.Label(self.window, text="", font=("Helvetica", 12), bg="#283593", fg="white")
        self.command_label.place(x=10, y=110)

        # Text input field for typing commands
        self.text_input_field = tk.Entry(self.window, font=("Helvetica", 14), width=40)
        self.text_input_field.place(x=10, y=150, width=550, height=40)

        # Submit Button for text input
        self.submit_button = ttk.Button(self.window, text=" ↵ Enter", style="TButton", command=self.submit_text_command)
        self.submit_button.place(x=590, y=150, width=150, height=40)

        # Bind the Enter key to trigger the text submission
        self.text_input_field.bind("<Return>", self.on_enter_pressed)

        self.output_frame = tk.Frame(self.window, bg="#303f9f", bd=2, relief="groove")
        self.output_frame.place(x=10, y=200, width=780, height=300)

        self.output_text = tk.Text(self.output_frame, wrap=tk.WORD, font=("Times New Roman", 14, "bold"), bg="#e8eaf6", fg="#1a237e", bd=0, padx=10, pady=10)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 14), padding=10)

        # Voice Input Button
        self.microphone_button = ttk.Button(self.window, text="🎤 Voice", style="TButton", command=self.run_voice_assistant)
        self.microphone_button.place(x=250, y=470, width=150, height=50)

        # Text Input Button
        self.text_button = ttk.Button(self.window, text="💬 Text", style="TButton", command=self.run_text_assistant)
        self.text_button.place(x=420, y=470, width=150, height=50)

        # Stop Button
        self.stop_button = ttk.Button(self.window, text="🛑 Stop", style="TButton", command=self.window.quit)
        self.stop_button.place(x=590, y=470, width=150, height=50)

    def run(self):
        """Run the Tkinter main loop"""
        self.window.mainloop()

    def run_voice_assistant(self):
        """Handle voice input and process the command"""
        threading.Thread(target=self.handle_voice_input).start()

    def handle_voice_input(self):
        """Handle voice command input in a separate thread"""
        command, recognized = self.assistant.take_command()
        self.command_label.config(text="You said: " + command)
        self.output_text.insert(tk.END, "You said: " + command + "\n")
        self.output_text.see(tk.END)  # Scroll to the end of the output
        if recognized:
            self.assistant.process_command(command)
        else:
            self.output_text.insert(tk.END, "Sorry, I didn't catch that.\n")
            self.output_text.see(tk.END)

    def run_text_assistant(self):
        """Activate text input field for typing command"""
        self.command_label.config(text="Enter your command:")
        self.output_text.insert(tk.END, "Waiting for text input...\n")
        self.output_text.update()

    def submit_text_command(self):
        """Handle text input submission"""
        command = self.text_input_field.get().lower()
        if command:
            self.command_label.config(text="You entered: " + command)
            self.output_text.insert(tk.END, "You entered: " + command + "\n")
            self.assistant.process_command(command)
            self.text_input_field.delete(0, tk.END)  # Clear the input field after submission
        else:
            self.command_label.config(text="Please enter a command.")
            self.output_text.insert(tk.END, "Please enter a command.\n")
            self.output_text.see(tk.END)  # Scroll to the end of the output

    def update_output(self, text):
        """Update the output_text widget with animated text (letter by letter) while speaking"""
        def insert_char(index=0):
            """Insert one character at a time with a small delay"""
            if index < len(text):
                self.output_text.insert(tk.END, text[index])
                self.output_text.see(tk.END)  # Scroll to the end
                self.window.after(10, insert_char, index + 1)  # Delay and call the function again

        insert_char(0)  # Start inserting the characters from the beginning

    def talk(self, text):
        """Speaks the given text and prints it on the screen letter by letter in real-time."""
        def speak():
            """Speak text and update output simultaneously."""
            self.assistant.engine.say(text)
            self.assistant.engine.runAndWait()

        # Run the speaking and text animation in parallel using threading
        threading.Thread(target=speak).start()
        self.update_output(text)  # Simultaneously update text in the GUI

    def on_enter_pressed(self, event=None):
        """Called when the Enter key is pressed."""
        self.submit_text_command()  # Trigger the same action as clicking the Submit button
