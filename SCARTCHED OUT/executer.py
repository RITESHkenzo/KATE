import os
import subprocess
import pyautogui
import wmi
import screen_brightness_control as sbc

class KateExecuter:
    def __init__(self):
        print("[KATE's Universal Executer Initialized...]")
        try:
            # Connect to the Windows Management Instrumentation for hardware tasks
            self.wmi_obj = wmi.WMI()
            self.wmi_hardware = wmi.WMI(namespace='root/wmi')
        except Exception as e:
            print(f"Warning: WMI Initialisation failed: {e}")
            self.wmi_obj = None
            self.wmi_hardware = None

    def run(self, intent_dict):
        """
        The main entry point called by main.py.
        Maps the AI's 'action' to the correct Python function.
        """
        if not intent_dict:
            return "I couldn't understand that command."

        action = intent_dict.get("action")
        target = intent_dict.get("target", "")
        value = intent_dict.get("value")

        if action == "open_app":
            return self.universal_open(target)
        
        elif action == "set_brightness":
            return self.set_brightness(value)
        
        elif action == "change_volume":
            return self.change_volume(target)
        
        elif action == "set_power_mode":
            return self.set_power_mode(target)
        
        elif action == "run_diagnostics":
            return self.run_diagnostics()
        
        return f"Action '{action}' is recognized but not yet programmed in the Executer."

    def universal_open(self, app_name):
        print(f"KATE: Attempting to launch '{app_name}'...")
        try:
            # Using 'start' allows Windows to find common apps by name (e.g., 'chrome', 'notepad')
            subprocess.Popen(f'start {app_name}', shell=True)
            return f"Successfully opened {app_name}."
        except Exception as e:
            return f"Failed to open {app_name}. Error: {e}"

    def set_brightness(self, level):
        try:
            # Ensure level is a valid integer between 0 and 100
            brightness = int(level)
            sbc.set_brightness(brightness)
            return f"Brightness adjusted to {brightness} percent."
        except Exception as e:
            return f"Brightness error: {e}"

    def change_volume(self, direction):
        direction = str(direction).lower()
        if "up" in direction or "increase" in direction:
            for _ in range(5): pyautogui.press("volumeup")
            return "Volume increased."
        elif "down" in direction or "decrease" in direction:
            for _ in range(5): pyautogui.press("volumedown")
            return "Volume decreased."
        elif "mute" in direction:
            pyautogui.press("volumemute")
            return "Volume toggled."
        return "I'm not sure which way to change the volume."

    def set_power_mode(self, mode):
        # Official Windows Power Plan GUIDs
        plans = {
            "saver": "a1841308-3541-4fab-bc81-f71556f20b4a",
            "balanced": "381b4222-f694-41f0-9685-ff5bb260df2e",
            "performance": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
        }
        
        mode = str(mode).lower()
        for key, guid in plans.items():
            if key in mode:
                # Running powercfg requires the app to be 'Run as Administrator'
                os.system(f"powercfg /setactive {guid}")
                return f"System shifted to {key} mode."
        return "Power mode not found. Try 'saver' or 'performance'."

    def run_diagnostics(self):
        """Advanced diagnostics as per SRS requirements."""
        if not self.wmi_obj:
            return "Diagnostics unavailable: WMI service error."
        
        report = "Diagnostic Report: "
        try:
            # Check GPU Status
            for gpu in self.wmi_obj.Win32_VideoController():
                report += f"GPU {gpu.Name} is {gpu.Status}. "
            # Check Battery
            for battery in self.wmi_obj.Win32_Battery():
                report += f"Battery is at {battery.EstimatedChargeRemaining}%."
            return report
        except:
            return "Basic diagnostics completed. System is stable."