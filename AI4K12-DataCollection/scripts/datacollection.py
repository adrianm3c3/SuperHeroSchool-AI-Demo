import os
from datetime import datetime

LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
os.makedirs(LOG_DIR, exist_ok=True)

class SessionLogger:
    def __init__(self, first_name, last_initial, grade):
        self.first_name = first_name
        self.last_initial = last_initial
        self.grade = grade
        self.filename = f"{first_name}_{last_initial}_Grade{grade}.txt"
        self.filepath = os.path.join(LOG_DIR, self.filename)

    def start_new_session(self):
        print(f"[DEBUG] Writing log to: {self.filepath}")
        try:
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write("\n" + "=" * 60 + "\n")
                f.write(f"New Session Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Student: {self.first_name} {self.last_initial}, Grade {self.grade}\n")
                f.write("=" * 60 + "\n\n")
            print(f"[SESSION STARTED] {self.filename}")
        except Exception as e:
            print(f"[ERROR] Failed to write log: {e}")

    def log_choice(self, choice, reason, tag):
        timestamp = datetime.now().strftime("%H:%M:%S")
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] Submission:\n")
            f.write(f"  Choice: {choice}\n")
            f.write(f"  Reason: {reason}\n")
            f.write(f"  Tag: {tag}\n\n")
        print(f"[LOGGED] Choice logged to {self.filename}")

    def set_prediction(self, prediction):
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write("=" * 50 + "\n")
            f.write(f"Final Prediction: {prediction.get('prediction', 'Unknown')}\n\n")
            f.write("Model Scenario Breakdown:\n")
            for i, scenario in enumerate(prediction.get("model_scenarios", []), 1):
                f.write(f"{i}. {scenario['prompt']}\n")
                f.write(f"   → Model Chose: {scenario['choice']} [{scenario['tag']}] (Confidence: {scenario['confidence']})\n")
            f.write("\nSession End: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        print(f"[FINALIZED] Prediction written to {self.filename}")
