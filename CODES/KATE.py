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

r = sr.Recognizer()
r.energy_threshold = 300
r.dynamic_energy_threshold = False
mic = sr.Microphone()

MAX_TURNS = 10
conversation: list[dict] = []


# ─── UI helpers ───────────────────────────────────────────────────────────────

def set_status(text: str):
    root.after(0, lambda: status.configure(text=text))


def log(text: str):
    root.after(0, lambda: (box.insert("end", text + "\n"), box.see("end")))


# ─── Speech ───────────────────────────────────────────────────────────────────

def say(text: str):
    """Speak text — BLOCKING so the mic doesn't open while KATE is still talking."""
    print("KATE:", text)
    log("KATE: " + text)
    engine = pyttsx3.init()
    engine.setProperty("rate", 170)
    engine.say(text)
    engine.runAndWait()          # blocks until speech is fully done


def listen() -> str:
    """Open the mic and return whatever was said (lowercase), or '' on failure."""
    with mic as source:
        print("Listening...")
        set_status("Listening...")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            return ""
        except OSError as e:
            print(f"Microphone error: {e}")
            return ""

    try:
        q = r.recognize_google(audio, language="en-in")
        q = q.lower().strip()
        print("Heard:", q)
        return q
    except sr.UnknownValueError:
        print("Not clear")
        return ""
    except sr.RequestError as e:
        print(f"Recognition service error: {e}")
        return ""


# ─── Wake word ────────────────────────────────────────────────────────────────

DIRECT_KEYWORDS = ("open", "play", "time", "google", "youtube", "file", "exit")


def wake():
    """
    Loop until a wake event:
      • "hi kate"      → returns None  (caller must listen for the command)
      • direct keyword → returns the raw query string (already IS the command)
    """
    while True:
        set_status("Waiting for wake word…")
        q = listen()

        if not q:
            continue

        if "hi kate" in q:
            say("yes")
            return None

        if any(word in q for word in DIRECT_KEYWORDS):
            print("Direct command detected:", q)
            return q


# ─── AI chat via Ollama ───────────────────────────────────────────────────────

def chat(q: str):
    global conversation
    set_status("Thinking…")

    conversation.append({"role": "user", "content": q})

    # keep at most MAX_TURNS pairs (user + assistant)
    if len(conversation) > MAX_TURNS * 2:
        conversation = conversation[-(MAX_TURNS * 2):]

    try:
        res = requests.post(
            "http://localhost:11434/api/chat",
            json={"model": "phi", "messages": conversation, "stream": False},
            timeout=15,
        )
        res.raise_for_status()
        ans = res.json()["message"]["content"]
        conversation.append({"role": "assistant", "content": ans})
        say(ans)

    except requests.exceptions.ConnectionError:
        say("I can't reach the AI server. Is Ollama running?")
    except requests.exceptions.Timeout:
        say("The AI took too long to respond.")
    except (KeyError, ValueError) as e:
        print(f"Unexpected API response: {e}")
        say("I got a strange response from the AI.")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        say("There was an error talking to the AI.")


# ─── Built-in commands ────────────────────────────────────────────────────────

def open_app(app: str):
    if not app:
        say("Which app should I open?")
        return
    try:
        os.startfile(app)
    except (FileNotFoundError, OSError):
        subprocess.Popen(["cmd", "/c", "start", "", app])
    say("opening " + app)


def files(q: str):
    if "create file" in q:
        raw_name = q.replace("create file", "").strip()
        name = os.path.basename(raw_name) + ".txt"
        if not name or name == ".txt":
            say("Please say a file name.")
            return
        with open(name, "w") as f:
            f.write("made by kate")
        say("file created: " + name)

    elif "delete file" in q:
        raw_name = q.replace("delete file", "").strip()
        name = os.path.basename(raw_name)
        if os.path.exists(name):
            os.remove(name)
            say("deleted " + name)
        else:
            say("file not found")


def play(q: str):
    song = q.replace("play", "").strip()
    if not song:
        say("What should I play?")
        return
    subprocess.Popen(
        ["cmd", "/c", "start", f"spotify:search:{song}"],
        shell=False
    )
    say("playing " + song)


def handle(q: str):
    q = q.lower().strip()
    print("FINAL COMMAND:", q)
    log("\nYou: " + q)

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
        root.after(600, root.destroy)

    else:
        chat(q)


# ─── Main loop ────────────────────────────────────────────────────────────────

def run():
    # Calibrate mic once before the loop
    set_status("Calibrating mic…")
    try:
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=1.5)
    except OSError as e:
        print(f"Mic calibration failed: {e}")

    say("assistant started")        # blocks until TTS finishes — safe to listen after this

    while True:
        result = wake()             # blocks until "hi kate" or direct keyword
        time.sleep(0.5)             # let the mic settle after KATE's reply ("yes")

        set_status("Listening for command…")

        if result is None:          # woke via "hi kate" → still need to hear the command
            q = listen()
        else:                       # direct command already captured in wake()
            q = result

        print("Final command:", q)

        if q:
            handle(q)
        else:
            set_status("Didn't catch that — try again")
            time.sleep(1.5)

        set_status("Idle")


def start():
    b1.configure(state="disabled")
    threading.Thread(target=run, daemon=True).start()


# ─── UI ───────────────────────────────────────────────────────────────────────

ctk.set_appearance_mode("dark")

root = ctk.CTk()
root.title("KATE Assistant")
root.geometry("600x500")

title_label = ctk.CTkLabel(root, text="KATE", font=("Arial", 35))
title_label.pack(pady=10)

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

b2 = ctk.CTkButton(frame, text="Exit", command=root.destroy, fg_color="red")
b2.grid(row=0, column=1, padx=10)

root.mainloop()
