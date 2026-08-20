import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

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

_model = genai.GenerativeModel(
    model_name="gemini-flash-latest",
    system_instruction=SYSTEM_PROMPT,
)


def get_bot_response(user_message: str, chat_history=None) -> str:
    try:
        history_for_gemini = []
        if chat_history:
            for turn in chat_history:
                gemini_role = "user" if turn.get("role") == "user" else "model"
                history_for_gemini.append({
                    "role": gemini_role,
                    "parts": [turn.get("message", "")]
                })

        chat = _model.start_chat(history=history_for_gemini)
        response = chat.send_message(user_message)
        return response.text.strip()

    except Exception as e:
        return f"Sorry, I ran into an error talking to the AI service: {e}"