import os
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
    try:
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

        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        reply = data["candidates"][0]["content"]["parts"][0]["text"]
        return reply.strip()

    except Exception as e:
        return f"Sorry, I ran into an error talking to the AI service: {e}"