import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash-lite:generateContent"
)

SYSTEM_PROMPT = """
You are CodeTutor AI, a friendly and patient programming tutor.

Your job:
1. Explain code clearly, line by line if needed, in simple beginner-friendly language.
2. Detect bugs/errors in code the user pastes, and explain the fix (don't just give the fix silently).
3. Answer programming concept questions with short, clear explanations and a small example.
4. Suggest practice coding problems suited to the user's stated skill level.

Rules:
- Keep explanations concise but complete.
- Use code blocks for any code you write.
- If unrelated to programming, gently redirect back to coding topics.
- Be encouraging — this is a learning tool for students.
"""


def get_bot_response(user_message: str, chat_history=None) -> str:
    contents = []

    if chat_history:
        for turn in chat_history:
            gemini_role = "user" if turn.get("role") == "user" else "model"
            contents.append({
                "role": gemini_role,
                "parts": [{"text": turn.get("message", "")}]
            })

    contents.append({
        "role": "user",
        "parts": [{"text": user_message}]
    })

    payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": contents
    }

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(
                f"{GEMINI_URL}?key={GEMINI_API_KEY}",
                json=payload,
                timeout=30
            )

            # If the service is temporarily overloaded, wait and retry
            if response.status_code == 503 and attempt < max_retries:
                time.sleep(1.5 * (attempt + 1))
                continue

            response.raise_for_status()
            data = response.json()
            reply = data["candidates"][0]["content"]["parts"][0]["text"]
            return reply.strip()

        except Exception as e:
            # Log the full error (including any sensitive details) only on the server console
            print(f"Gemini API error (attempt {attempt + 1}): {e}")

            # Only return this generic, safe message to the user — never the raw exception
            if attempt == max_retries:
                return "Sorry, the AI service is busy right now. Please try again in a moment."