import os
import sys
import logging
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

# Setup
sys.path.append(os.path.join(os.path.dirname(__file__), "scripts"))
from scripts.app import process_submission, restart
from scripts.datacollection import SessionLogger

app = Flask(__name__)
app.secret_key = "super-secret-hero-key"
app.url_map.strict_slashes = False


logging.basicConfig(level=logging.DEBUG)

@app.before_request
def trace_everything():
    print(f"[TRACE] {request.method} {request.path}")


@app.route("/")
def home():
    print("==> GET / (home page)")
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        print("==> POST /login triggered")

        first_name = request.form.get("first_name")
        last_initial = request.form.get("last_initial")
        grade = request.form.get("grade")

        print(f"[DEBUG] Got form data: {first_name}, {last_initial}, Grade {grade}")

        logger = SessionLogger(first_name, last_initial, grade)
        logger.start_new_session()

        session["first_name"] = first_name
        session["last_initial"] = last_initial
        session["grade"] = grade
        session["user_choices"] = []
        session["user_reasons"] = []
        session["user_tags"] = []

        restart()
        return render_template("index.html")

    print("==> GET /login triggered")
    return render_template("login.html")


@app.route("/submit", methods=["POST"])
def submit_choice():
    print("==> /submit route triggered")

    data = request.json
    choice = data.get("choice") or "0"
    reason = data.get("reason") or ""
    scenario = data.get("scenario")

    logger = SessionLogger(session["first_name"], session["last_initial"], session["grade"])
    result = process_submission(choice, reason, scenario, logger=logger)

    if choice and reason:
        tag = result.get("tag", "none")
        session["user_choices"].append(choice)
        session["user_reasons"].append(reason)
        session["user_tags"].append(tag)

    return jsonify(result)

if __name__ == "__main__":
    print("Flask server starting...")
    app.run(debug=True)
