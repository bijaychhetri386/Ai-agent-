"""
JARVIS 2.0 - Personal Voice and Text Assistant

Features:
- Voice input and spoken responses
- Text mode
- Open websites and Google searches
- AI-powered answers through the OpenAI API
- Time and date
- Calculator
- Saved notes
- Session conversation context

Setup:
    pip install SpeechRecognition pyttsx3 pyaudio openai

Set OPENAI_API_KEY as an environment variable before using AI responses.
"""

import os
import ast
import operator
import webbrowser
from datetime import datetime

import speech_recognition as sr
import pyttsx3
from openai import OpenAI


# -------------------- SETTINGS --------------------

ASSISTANT_NAME = "jarvis"
AI_MODEL = "gpt-4o-mini"
NOTES_FILE = "jarvis_notes.txt"

WEBSITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "instagram": "https://www.instagram.com",
    "facebook": "https://www.facebook.com",
    "github": "https://github.com",
    "gmail": "https://mail.google.com",
}

MUSIC = {
    "believer": "https://www.youtube.com/results?search_query=Imagine+Dragons+Believer",
    "perfect": "https://www.youtube.com/results?search_query=Ed+Sheeran+Perfect",
    "shape of you": "https://www.youtube.com/results?search_query=Ed+Sheeran+Shape+of+You",
}

recognizer = sr.Recognizer()

try:
    voice = pyttsx3.init()
    voice.setProperty("rate", 180)
    voice.setProperty("volume", 1.0)
except Exception:
    voice = None

api_key = os.getenv("OPENAI_API_KEY")
ai_client = OpenAI(api_key=api_key) if api_key else None

conversation = [
    {
        "role": "system",
        "content": (
            "You are Jarvis, a helpful personal AI assistant. "
            "Answer clearly, accurately, and naturally."
        ),
    }
]


# -------------------- VOICE FUNCTIONS --------------------

def speak(message):
    """Display a response and speak it aloud."""
    print(f"\nJARVIS: {message}")

    if voice:
        try:
            voice.say(message)
            voice.runAndWait()
        except Exception as error:
            print("Speech output error:", error)


def listen():
    """Listen through the microphone and convert speech into text."""
    try:
        with sr.Microphone() as source:
            print("\nListening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.4)
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=8
            )

        words = recognizer.recognize_google(audio)
        print("YOU:", words)
        return words.lower().strip()

    except sr.WaitTimeoutError:
        return ""

    except sr.UnknownValueError:
        speak("I did not understand. Please try again.")
        return ""

    except sr.RequestError:
        speak("The speech recognition service is unavailable.")
        return ""

    except Exception as error:
        print("Microphone error:", error)
        return ""


# -------------------- AI FUNCTION --------------------

def ask_ai(question):
    """Send a question to the AI model and keep recent conversation context."""
    if ai_client is None:
        return "AI is not configured. Please set your OPENAI_API_KEY."

    conversation.append({"role": "user", "content": question})

    try:
        messages = [conversation[0]] + conversation[-10:]

        result = ai_client.chat.completions.create(
            model=AI_MODEL,
            messages=messages,
            max_tokens=300
        )

        answer = result.choices[0].message.content
        answer = answer.strip() if answer else "I could not create an answer."

        conversation.append({"role": "assistant", "content": answer})
        return answer

    except Exception as error:
        conversation.pop()
        return f"I could not connect to the AI service: {error}"


# -------------------- SAFE CALCULATOR --------------------

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def calculate(expression):
    """Calculate basic arithmetic without using eval()."""

    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
            left = evaluate(node.left)
            right = evaluate(node.right)

            if isinstance(node.op, ast.Pow) and abs(right) > 8:
                raise ValueError("Exponent is too large.")

            return _ALLOWED_OPERATORS[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
            return _ALLOWED_OPERATORS[type(node.op)](evaluate(node.operand))

        raise ValueError("Only basic arithmetic is supported.")

    try:
        tree = ast.parse(expression, mode="eval")
        return evaluate(tree.body)
    except Exception:
        return "I could not calculate that expression."


# -------------------- NOTES --------------------

def save_note(note):
    """Save a note with the current date and time."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(NOTES_FILE, "a", encoding="utf-8") as file:
            file.write(f"[{timestamp}] {note}\n")
        return "Your note has been saved."
    except OSError:
        return "I could not save your note."


def read_notes():
    """Read notes saved in the notes file."""
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as file:
            notes = file.read().strip()
        return notes if notes else "You have no saved notes."
    except FileNotFoundError:
        return "You have no saved notes yet."


# -------------------- COMMAND HANDLER --------------------

def handle_command(command):
    """Choose an action based on the user's command."""
    command = command.lower().strip()

    if not command:
        return ""

    if command in {"exit", "quit", "goodbye", "shutdown"}:
        return "EXIT"

    if command in {"help", "commands"}:
        return (
            "You can ask questions, open websites, search Google, play music, "
            "check the time or date, calculate, save notes, or read your notes."
        )

    if "time" in command:
        return "The time is " + datetime.now().strftime("%I:%M %p")

    if "date" in command:
        return "Today is " + datetime.now().strftime("%A, %B %d, %Y")

    if command.startswith("open "):
        site = command[5:].strip()
        if site in WEBSITES:
            webbrowser.open(WEBSITES[site])
            return f"Opening {site}."
        return "That website is not in my saved website list."

    if command.startswith("search for "):
        query = command.removeprefix("search for ").strip()
        url = "https://www.google.com/search?q=" + query.replace(" ", "+")
        webbrowser.open(url)
        return f"Searching Google for {query}."

    if command.startswith("play "):
        song = command[5:].strip()
        if song in MUSIC:
            webbrowser.open(MUSIC[song])
            return f"Opening a search for {song}."
        return "I do not have that song saved yet."

    if command.startswith("calculate "):
        expression = command.removeprefix("calculate ").strip()
        return f"The answer is {calculate(expression)}."

    if command.startswith("take a note "):
        note = command.removeprefix("take a note ").strip()
        return save_note(note) if note else "Please tell me what to save."

    if command in {"read my notes", "show notes"}:
        return read_notes()

    if command == "clear conversation":
        conversation[:] = [conversation[0]]
        return "I cleared the conversation history for this session."

    return ask_ai(command)


# -------------------- MAIN PROGRAM --------------------

def main():
    speak("Jarvis 2.0 is ready.")

    mode = input("Choose interaction mode (voice/text): ").lower().strip()
    if mode not in {"voice", "text"}:
        mode = "text"

    speak(f"{mode.capitalize()} mode activated. Type or say help for commands.")

    while True:
        if mode == "voice":
            spoken_command = listen()

            if not spoken_command:
                continue

            # Require the wake word before processing a voice command.
            if ASSISTANT_NAME not in spoken_command:
                continue

            command = spoken_command.replace(ASSISTANT_NAME, "", 1).strip()

            if not command:
                speak("Yes? What can I do for you?")
                continue
        else:
            command = input("\nYOU: ").strip().lower()

        if command == "voice mode":
            mode = "voice"
            speak("Voice mode activated.")
            continue

        if command == "text mode":
            mode = "text"
            speak("Text mode activated.")
            continue

        response = handle_command(command)

        if response == "EXIT":
            speak("Goodbye. Jarvis is shutting down.")
            break

        if response:
            speak(response)


if __name__ == "__main__":
    main()
