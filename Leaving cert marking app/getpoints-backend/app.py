import os
import requests
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / '.env')

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

AI_PROVIDER = os.environ.get("AI_PROVIDER", "anthropic").lower()
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
DEMO_MODE = os.environ.get("DEMO_MODE", "true").lower() == "true"

if AI_PROVIDER == "anthropic" and not ANTHROPIC_API_KEY and not DEMO_MODE:
    raise RuntimeError("Please set ANTHROPIC_API_KEY in your .env file or enable DEMO_MODE.")

if AI_PROVIDER == "openai" and not OPENAI_API_KEY and not DEMO_MODE:
    raise RuntimeError("Please set OPENAI_API_KEY in your .env file or enable DEMO_MODE.")

PROMPT_TEMPLATE = """
You are grading a Leaving Cert Higher Maths answer using SEC-style marking.
The output must be structured and explain mark allocation like:
- Method: X/Y
- Accuracy: X/Y
- Final Answer: X/Y
- Feedback: ...
- Common mistakes: ...

Question:
{question}

Student answer:
{answer}

Grade the response exactly like an SEC examiner would, focusing on method, accuracy, and final answer. If the answer is wrong, explain which part lost marks.
"""

@app.route("/api/grade", methods=["POST"])
def grade_answer():
    try:
        data = request.get_json(force=True)
        question = data.get("question", "").strip()
        answer = data.get("answer", "").strip()

        if not question or not answer:
            return jsonify({"error": "Both question and answer are required."}), 400

        prompt = PROMPT_TEMPLATE.format(question=question, answer=answer)

        if AI_PROVIDER == "anthropic":
            if not ANTHROPIC_API_KEY:
                if DEMO_MODE:
                    text = "Method: 3/4\nAccuracy: 2/3\nFinal Answer: 0/3\nFeedback: The method is partly correct, but the final result is missing the required y-coordinate verification.\nCommon mistakes: Forgetting to calculate the y-values for stationary points."
                else:
                    raise RuntimeError("Please set ANTHROPIC_API_KEY in your .env file.")
            else:
                payload = {
                    "model": "claude-opus-4-8",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 600,
                }
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                }
                try:
                    response = requests.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers, timeout=30)
                    response.raise_for_status()
                    result = response.json()
                    if isinstance(result.get("content"), list):
                        text_blocks = [
                            block.get("text", "")
                            for block in result["content"]
                            if isinstance(block, dict)
                        ]
                        text = " ".join([t for t in text_blocks if t]).strip()
                    else:
                        text = result.get("completion", result.get("message", {}).get("content", ""))
                except requests.exceptions.RequestException as exc:
                    error_body = exc.response.text if exc.response is not None else str(exc)
                    print("Anthropic API request failed:", error_body)
                    if exc.response is not None:
                        print("Status code:", exc.response.status_code)
                    return jsonify({"error": "Anthropic API error", "details": error_body}), 502

        else:
            if not OPENAI_API_KEY:
                if DEMO_MODE:
                    text = "Method: 3/4\nAccuracy: 2/3\nFinal Answer: 0/3\nFeedback: The method is partly correct, but the final result is missing the required y-coordinate verification.\nCommon mistakes: Forgetting to calculate the y-values for stationary points."
                else:
                    raise RuntimeError("Please set OPENAI_API_KEY in your .env file.")
            else:
                payload = {
                    "model": "gpt-4.1",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 800,
                }
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                }
                try:
                    response = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=30)
                    response.raise_for_status()
                    result = response.json()
                    text = result["choices"][0]["message"]["content"]
                except requests.exceptions.RequestException as exc:
                    error_body = exc.response.text if exc.response is not None else str(exc)
                    print("OpenAI API request failed:", error_body)
                    if exc.response is not None:
                        print("Status code:", exc.response.status_code)
                    return jsonify({"error": "OpenAI API error", "details": error_body}), 502
    except Exception as exc:
        return jsonify({"error": "server_error", "details": str(exc)}), 500

    return jsonify({"success": True, "grading": text})

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "provider": AI_PROVIDER})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
