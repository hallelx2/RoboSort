# importing the pyttsx library
import pyttsx3
from time import sleep

# initialisation
engine = pyttsx3.init()


def speak_waste_type(waste):
    return engine.say(f"I am picking a {waste}")


def done_picking(waste):
    return engine.say(f"I am done picking a {waste}")


speak_waste_type("plastic")
done_picking("plastic")

engine.runAndWait()
