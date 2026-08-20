import os
import uuid
from flask import Flask, render_template, request, jsonify, session

from chatbot_config import get_bot_response

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

CHAT_STORE = {}


def get_session_id():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return session["session_id"]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    session_id = get_session_id()
    prior_history = CHAT_STORE.get(session_id, [])

    bot_reply = get_bot_response(user_message, chat_history=prior_history)

    prior_history.append({"role": "user", "message": user_message})
    prior_history.append({"role": "bot", "message": bot_reply})
    CHAT_STORE[session_id] = prior_history

    return jsonify({"reply": bot_reply})


@app.route("/history", methods=["GET"])
def history():
    session_id = get_session_id()
    return jsonify({"history": CHAT_STORE.get(session_id, [])})


if __name__ == "__main__":
    app.run(debug=True, port=5000)