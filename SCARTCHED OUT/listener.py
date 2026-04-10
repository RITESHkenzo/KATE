import speech_recognition as sr

class KateListener:
    def __init__(self):
        # Initialize the recognizer and microphone
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Set a few sensitivity parameters
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # Seconds of silence before a phrase is considered complete
        
        print("[KATE's Listener Initialized...]")

    def listen(self):
        """
        Captures audio from the microphone and converts it to text using Google Speech Recognition.
        """
        with self.microphone as source:
            # Calibrate for 1 second to handle background fan noise/static
            print("\n[Listening] ...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            try:
                # timeout: How long to wait for speech to start
                # phrase_time_limit: Max length of a single command
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                print("[Processing] Converting voice to text...")
                # Recognize speech using Google (requires internet)
                query = self.recognizer.recognize_google(audio)
                print(f"[Captured] You said: '{query}'")
                return query.lower()

            except sr.WaitTimeoutError:
                # Happens if no speech is detected within the 'timeout' period
                return None
            
            except sr.UnknownValueError:
                # Happens if speech is heard but the engine can't decipher the words
                print("[Listener] Sorry, I couldn't understand that sound.")
                return None
            
            except sr.RequestError as e:
                # Happens if there is no internet connection or the API is down
                print(f"[Listener] Could not request results; check your internet. {e}")
                return None
            
            except Exception as e:
                # Catch-all for other hardware/permission errors
                print(f"[Listener] Hardware Error: {e}")
                return None

# --- Internal Test ---
if __name__ == "__main__":
    test_listener = KateListener()
    print("Testing Listener. Say something...")
    result = test_listener.listen()
    print(f"Result: {result}")