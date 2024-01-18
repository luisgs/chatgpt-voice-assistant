import os
from openai import OpenAI
import time
import speech_recognition as sr
import pyttsx3
import numpy as np
import logging
import traceback
import sys
# from os.path import join, dirname
# import matplotlib.pyplot as plt
# ^ matplotlib is great for visualising data and for testing purposes but usually not needed for production

# Logging as output logging messages.
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

if os.environ.get("OPENAI_API_KEY") is not None:
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
else:
    logging.error("ERROR: OpenAI API Key is not INITIALIZED/FOUND as OS VARIABLE: OpenAI_API_Key")
    exit()

# model = 'gpt-3.5-turbo-1106'
# Set up the speech recognition and text-to-speech engines
r = sr.Recognizer()
engine = pyttsx3.init()
voice = engine.getProperty('voices')[1]
engine.setProperty('voice', voice.id)
name = "John Doe"
welcome = [f"Hello there! My name is {name}. Im ready!"]
greetings = [f"whats up master {name}",
             "yeah?",
             "Well, hello there, Master of Puns and Jokes - how's it going today?",
             f"Ahoy there, Captain {name}! How's the ship sailing?",
             f"Bonjour, Monsieur {name}! Comment ça va? Wait, why the hell am I speaking French?" ]

# Listen for the wake word "hey pos"
def listen_for_wake_word(source):
    wake_up_word = "hello king"

    logging.info(f"Listening for the wake up word: '{wake_up_word}'...")
    engine.say(np.random.choice(welcome))

    while True:
        try:
            logging.info("Listening...")
            audio = r.listen(source)
        except:
            logging.error("ERROR: something happen while listening. Script is stopped")
            break

        try:
            text = r.recognize_google(audio)
            text = wake_up_word     # for testing
            if wake_up_word in text.lower():
                logging.info("Wake word detected.")
                engine.say(np.random.choice(greetings))
                engine.runAndWait()
                listen_and_respond(source)
                break
            else:

                logging.info("Wake word NOT detected.")
        except sr.UnknownValueError:
            pass

# Listen for input and respond with OpenAI API
def listen_and_respond(source):
    logging.info("Listening...")

    while True:
        try:
            logging.info("Listening...")
            audio = r.listen(source)
        except:
            logging.error("ERROR: something happen while listening. Script is stopped")
            break
        try:
            text = r.recognize_google(audio)
            logging.info(f"You said: {text}")
            if not text:
                continue

            # Send input to OpenAI API
            # response = client.completions.create(model='curie')
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[{"role": "system", "content": text}],
            )
            response_text = response.choices[0].message.content
            logging.info(f"OpenAI response: {response_text}")

            # Speak the response
            engine.say(response_text)
            engine.runAndWait()

            if not audio:
                listen_for_wake_word(source)
        except sr.UnknownValueError:
            time.sleep(2)
            logging.info("Silence found, shutting up, listening...")
            listen_for_wake_word(source)
            break

        except sr.RequestError as e:
            logging.info(f"Could not request results; {e}")
            engine.say(f"Could not request results; {e}")
            engine.runAndWait()
            listen_for_wake_word(source)
            break

# Use the default microphone as the audio source
with sr.Microphone() as source:
    listen_for_wake_word(source)
