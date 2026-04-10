import json
from google import genai
from google.genai import types

class KateBrain:
    def __init__(self):
        # 1. ENTER YOUR API KEY HERE
        self.api_key = "AIzaSyARucYm1qxXEizEdUq9WgggZkCxUom2MCA"
        
        # 2. Initialize the 2026 GenAI Client
        self.client = genai.Client(api_key=self.api_key)
        
        # 3. Define System Instructions (The "Identity" of the Brain)
        self.sys_config = types.GenerateContentConfig(
            system_instruction=(
                "You are the logic engine for KATE (Keyboard & Audio Task Executer). "
                "Your job is to translate human speech into system-level JSON commands. "
                "ONLY respond with a JSON object. Do not include conversational text. "
                "Available Actions: "
                "1. 'open_app' (target: app name like 'chrome', 'calculator', 'f122') "
                "2. 'set_brightness' (value: integer 0-100) "
                "3. 'set_power_mode' (target: 'saver', 'balanced', or 'performance') "
                "4. 'change_volume' (target: 'up', 'down', or 'mute') "
                "5. 'run_diagnostics' (target: 'system') "
            ),
            response_mime_type='application/json', # Strictly enforce JSON output
            temperature=0.1 # Keep responses consistent and predictable
        )

    def analyze(self, user_text):
        """
        Sends the transcribed voice text to Gemini and returns a clean dictionary.
        """
        if not user_text or len(user_text.strip()) < 2:
            return {"action": "none"}

        try:
            # 4. Generate the command logic
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=user_text,
                config=self.sys_config
            )
            
            # 5. Parse the AI's JSON response into a Python Dictionary
            logic_dict = json.loads(response.text)
            print(f"[Brain Logic] Interpreted as: {logic_dict}")
            return logic_dict

        except Exception as e:
            print(f"[Brain Error] Logic parsing failed: {e}")
            # Fallback if the AI fails or quota is hit
            return {"action": "unknown", "error": str(e)}

# --- Internal Test (Only runs if you execute brain.py directly) ---
if __name__ == "__main__":
    # Quick test to see if your API key works
    test_brain = KateBrain()
    print(test_brain.analyze("Open chrome and turn the brightness to 80 percent"))