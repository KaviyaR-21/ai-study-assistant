import os
import json
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(timeout=60000),
)
MODEL = "gemini-flash-lite-latest"

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/explain", methods=["POST"])
def explain():
    topic = request.get_json().get("topic", "").strip()
    if not topic:
        return jsonify({"error": "Please enter a topic."}), 400

    prompt = f'Explain "{topic}" simply for a beginner. Give a short explanation, one example, and 3 key points.'

    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return jsonify({"result": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/questions", methods=["POST"])
def questions():
    topic = request.get_json().get("topic", "").strip()
    if not topic:
        return jsonify({"error": "Please enter a topic."}), 400

    prompt = f'Create 5 practice questions about "{topic}" for a beginner. Number them 1 to 5. After the questions, add an "Answers" section with a short answer for each.'

    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return jsonify({"result": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/quiz", methods=["POST"])
def quiz():
    topic = request.get_json().get("topic", "").strip()
    if not topic:
        return jsonify({"error": "Please enter a topic."}), 400

    prompt = f'''Create 5 beginner multiple choice questions about "{topic}".
Return ONLY a JSON array. Each item must be exactly:
{{"question": "text", "options": ["opt1", "opt2", "opt3", "opt4"], "answer": 0}}
"answer" is the index (0 to 3) of the correct option.'''

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        return jsonify({"quiz": json.loads(response.text)})
    except json.JSONDecodeError:
        return jsonify({"error": "AI returned an invalid quiz. Try again."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
if __name__ == "__main__":
    app.run(debug=True)