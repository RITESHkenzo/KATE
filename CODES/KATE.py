import speech_recognition as sr
import pyttsx3
import os
import webbrowser
import datetime
import requests
import subprocess
import threading
import time
import customtkinter as ctk

engine = pyttsx3.init()
engine.setProperty('rate', 170)

chatStr = ""

# UI status
def set_status(text):
    status.configure(text=text)

# speak
def say(text):
    print("KATE:", text)
    box.insert("end", "KATE: " + text + "\n")
    box.see("end")
    engine.say(text)
    engine.runAndWait()

# listen
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        set_status("Listening...")
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)

    try:
        q = r.recognize_google(audio, language="en-in")
        q = q.lower()
        print("Heard:", q)
        return q
    except:
        print("Not clear")
        return ""

# wake word = h or o
def wake():
    while True:
        q = listen()
        print("Wake heard:", q)

        if "h" in q or "o" in q:
            say("yes")
            break

# AI
def chat(q):
    global chatStr
    set_status("Thinking...")

    chatStr += "User: " + q + "\nKATE: "

    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "phi", "prompt": chatStr, "stream": False}
        )

        ans = res.json()["response"]
        say(ans)
        chatStr += ans + "\n"

    except:
        say("ai error")

# apps
def open_app(app):
    os.system("start " + app)
    say("opening " + app)

# files
def files(q):
    if "create file" in q:
        name = q.replace("create file", "").strip() + ".txt"
        with open(name, "w") as f:
            f.write("made by kate")
        say("file created")

    elif "delete file" in q:
        name = q.replace("delete file", "").strip()
        if os.path.exists(name):
            os.remove(name)
            say("deleted")
        else:
            say("not found")

# spotify
def play(q):
    song = q.replace("play", "").strip()
    subprocess.Popen("start spotify:search:" + song, shell=True)
    say("playing " + song)

# commands
def handle(q):
    print("FINAL COMMAND:", q)
    box.insert("end", "\nYou: " + q + "\n")

    q = q.replace("from", "chrome")

    if "youtube" in q:
        webbrowser.open("https://youtube.com")
        say("opening youtube")

    elif "google" in q:
        webbrowser.open("https://google.com")
        say("opening google")

    elif "time" in q:
        t = datetime.datetime.now().strftime("%H:%M")
        say("time is " + t)

    elif "play" in q:
        play(q)

    elif "open" in q:
        app = q.replace("open", "").strip()
        open_app(app)

    elif "file" in q:
        files(q)

    elif "exit" in q:
        say("bye")
        os._exit(0)

    else:
        chat(q)

# main loop
def run():
    say("assistant started")

    while True:
        set_status("Waiting...")
        wake()

        time.sleep(1)

        set_status("Processing...")
        q = listen()

        print("After wake:", q)

        if q != "":
            handle(q)
        else:
            print("No command")

        set_status("Idle")

# thread
def start():
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()

# UI
ctk.set_appearance_mode("dark")

root = ctk.CTk()
root.title("Assistant")
root.geometry("600x500")

title = ctk.CTkLabel(root, text="Assistant", font=("Arial", 35))
title.pack(pady=10)

orb = ctk.CTkLabel(root, text="●", font=("Arial", 90), text_color="cyan")
orb.pack()

status = ctk.CTkLabel(root, text="Idle")
status.pack(pady=5)

box = ctk.CTkTextbox(root, height=180, width=500)
box.pack(pady=10)

frame = ctk.CTkFrame(root)
frame.pack(pady=10)

b1 = ctk.CTkButton(frame, text="Start", command=start)
b1.grid(row=0, column=0, padx=10)

b2 = ctk.CTkButton(frame, text="Exit", command=root.quit, fg_color="red")
b2.grid(row=0, column=1, padx=10)

root.mainloop()