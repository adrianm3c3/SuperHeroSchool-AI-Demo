from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
label_encoder = LabelEncoder()
classifier = LogisticRegression(max_iter=1000)

def train_classifier(prompts, tags, reasons, option_texts, option_tags):
    X, y = [], []
    print("\n=== [TRAINING DEBUG START] ===")
    for reason, tag, opts in zip(reasons, tags, option_texts):
        if not tag or tag == "none":
            continue
        text = reason.strip() + " " + opts[0].strip()
        emb = embedding_model.encode(text)
        X.append(emb)
        y.append(tag)
        print(f"[TRAIN] '{text}' → {tag}")
    print(f"[TRAINING SET SIZE] {len(X)}")
    print("=== [TRAINING DEBUG END] ===\n")

    if not X:
        return None, None
    y_encoded = label_encoder.fit_transform(y)
    classifier.fit(X, y_encoded)
    return embedding_model, classifier

def predict_model_choices(train_scenarios, tags, reasons, model_scenarios):
    prompts = [s["prompt"] for s in train_scenarios]
    option_texts = [
        [opt["text"]] for s in train_scenarios
        for opt in s["options"]
        if "_".join(sorted(opt.get("tags", []))) == tags[train_scenarios.index(s)]
    ]
    option_tags = [[opt.get("tags", []) for opt in s["options"]] for s in train_scenarios]

    model, clf = train_classifier(prompts, tags, reasons, option_texts, option_tags)
    if not model:
        return []

    model_choices = []
    print("\n=== [MODEL PREDICTIONS] ===")
    for i, scenario in enumerate(model_scenarios):
        best_tag = None
        best_score = -1
        best_text = None
        options = scenario["options"]

        for opt in options:
            text = opt["text"]
            emb = model.encode(text)
            pred = clf.predict([emb])[0]
            prob = max(clf.predict_proba([emb])[0])
            tag = label_encoder.inverse_transform([pred])[0]

            print(f"[{i+1}] '{text}' → {tag} ({prob:.2f})")

            if prob > best_score:
                best_score = prob
                best_tag = tag
                best_text = text

        model_choices.append({
            "text": best_text,
            "tag": best_tag,
            "confidence": round(best_score, 2)
        })

    return model_choices
