import os
import json
import random
from prediction import train_classifier, predict_model_choices

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCENARIOS_PATH = os.path.join(SCRIPT_DIR, "..", "scenarios")
USER_SCENARIOS_PATH = os.path.join(SCENARIOS_PATH, "UserScenarios.json")
MODEL_SCENARIOS_PATH = os.path.join(SCENARIOS_PATH, "ModelScenarios.json")

user_choices = []
user_reasons = []
user_tags = []
current_index = 0

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_user_scenarios():
    return load_json(USER_SCENARIOS_PATH)

def load_model_scenarios():
    return load_json(MODEL_SCENARIOS_PATH)

def restart():
    global current_index, user_choices, user_reasons, user_tags
    current_index = 0
    user_choices = []
    user_reasons = []
    user_tags = []

def process_submission(choice, reason, _, logger=None):
    global current_index, user_choices, user_reasons, user_tags

    user_scenarios = load_user_scenarios()
    total_user = len(user_scenarios)

    if current_index < total_user:
        scenario = user_scenarios[current_index]
        options = scenario["options"]

        if choice and reason:
            index = int(choice) - 1
            user_choices.append(choice)
            user_reasons.append(reason)
            tags = options[index].get("tags", [])
            tag_string = "_".join(sorted(tags)) if tags else "none"
            user_tags.append(tag_string)
            current_index += 1

           
            if logger:
                logger.log_choice(choice, reason, tag_string)

        if current_index < total_user:
            next_scenario = user_scenarios[current_index]
            return {
                "scenario": next_scenario["prompt"],
                "choices": [opt["text"] for opt in next_scenario["options"]],
                "image": next_scenario["imagePath"],
                "index": current_index
            }

    if current_index == total_user:
        print("[INFO] Training complete. Predicting model choices...")
        prediction = predict_model_response(user_scenarios, user_tags, user_reasons)

       
        if logger:
            logger.set_prediction(prediction)

        return prediction

    return {"error": "Invalid state."}

def predict_model_response(user_scenarios, tags, reasons):
    model_scenarios = load_model_scenarios()
    model_choices = predict_model_choices(user_scenarios, tags, reasons, model_scenarios)

    final_tags = [c["tag"] for c in model_choices if c["tag"] != "none"]
    final_tag = max(set(final_tags), key=final_tags.count) if final_tags else "none"

    scenario_breakdown = []
    for i, (s, pred) in enumerate(zip(model_scenarios, model_choices)):
        scenario_breakdown.append({
            "prompt": s["prompt"],
            "choice": pred["text"],
            "tag": pred["tag"],
            "confidence": pred["confidence"]
        })

    return {
        "final": True,
        "scenario": f"The model thinks you're a {final_tag.replace('_', ' ')} hero!",
        "prediction": final_tag,
        "model_scenarios": scenario_breakdown
    }
