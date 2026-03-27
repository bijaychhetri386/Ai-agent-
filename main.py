import speech_recognition as sr
import pyttsx3
import webbrowser
import pyaudio
from datetime import datetime
import musiclibrary
from openai import OpenAI
import os

recognizer = sr.Recognizer()
current_datetime=datetime.now().time()


def speak(text):
    engine = pyttsx3.init('sapi5')
    print("Jarvis:", text)
    engine.say(text)
    engine.runAndWait()
def aiprocess(command):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    completion=client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role":"system","content":"You are a virtual assistant named jarvis skilled in generak tasks like ALexa and Google Cloud"},
            {"role":"user","content":command}
    ]
    )
    
    return completion.choices[0].message.content
music={
    "shape of you":"https://youtu.be/JGwWNGJdvx8?si=558W2aqrq87m0LRn",
    "cry":"https://youtu.be/3XqqkrJENB4?si=gbGv3wiepZq3vAA6",
    "meri paro":"https://youtu.be/DxsDekHDKXo?si=OWJBSKQ5ffy1SFDl",
    "dafa":"https://youtu.be/SxTYjptEzZs?si=PpeQhrp2vE96ktyS"
}  

speak("I am jarvis 2.0. Identify yourself")

while True:
    try:
        while True:
            with sr.Microphone() as source:
                print("Jarvis is waiting to be activated:")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, phrase_time_limit=2)
            try:
                command = recognizer.recognize_google(audio).lower()
                print("You said:", command)

                if "point break" in command:
                    speak("Activated sucessfully")
                    print("jarvis activated successfully")
                    break
                
                #loop breaked and now it goes to next while loop!

                else:
                    speak("Access denied!.")

            except sr.UnknownValueError:
                speak("I didn't catch that. Please say the code again")
        
        
        while True:
        #wake word detection
                with sr.Microphone() as source:
                    print("Jarvis is listening....")
                    audio=recognizer.listen(source)
                try:
                    command = recognizer.recognize_google(audio).lower()
                    print("You said:", command)
                    if "what's your name" in command:
                        speak("I am Jarvis 2.0. Developed by BJ!")
                    elif "open google" in command:
                        speak("Opening google sir")
                        webbrowser.open("https://google.com")
                    elif "open youtube" in command:
                        speak("Opening youtube sir")
                        webbrowser.open("https://youtube.com")
                    elif "open instagaram" in command:
                        speak("Opening instagram sir")
                        webbrowser.open("https://instagram.com")
                    elif "open facebook" in command:
                        speak("Opening facebook sir")
                        webbrowser.open("https://facebook.com")
                    elif "current time" in command:
                        current_time = datetime.now().strftime("%H:%M")
                        speak(f"currrent time is {current_datetime}")
                    elif command.lower().startswith("play"):
                        song=command.lower().split(" ")[1]
                        link= musiclibrary.music[song]
                        webbrowser.open(link)
                    else:
                        output=aiprocess(command)
                        speak(output)
                except sr.UnknownValueError:
                    print("Could not understand")
                except Exception as e:
                    print("Error:", e)
           

            
#let open A.I handle the request
    
    except sr.UnknownValueError:
        print("Could not understand")

    except Exception as e:
        print("Error:", e)
        