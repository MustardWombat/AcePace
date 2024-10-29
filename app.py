from flask import Flask, request, jsonify, render_template
import openai
import os
from dotenv import load_dotenv

# Load environment variables from key.env
load_dotenv("Key.env")

app = Flask(__name__)

# Access the OpenAI API key from the environment
openai.api_key = os.getenv("OPENAI_API_KEY")
print("API Key:", openai.api_key)

#handles displaying the html file
@app.route("/")
def index():
    return render_template("index.html")


#Handles generating the quiz
@app.route("/generate_quiz", methods=["POST"])
def generate_quiz():
    data = request.json
    class_material = data.get("text", "")

    if not class_material:
        return jsonify({"error": "No class material provided"}), 400

    if not openai.api_key:
        return jsonify({"error": "OpenAI API key not found. Please check your environment variable."}), 500

    prompt = f"Generate a quiz with multiple-choice questions from the following material:\n{class_material}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        # Extract the response content
        response_text = response['choices'][0]['message']['content']
        questions = response_text.strip().split("\n\n")
        quiz_questions = []

        # Inside generate_quiz
        for question in questions:
            parts = question.split("\n")
            q_text = parts[0] if parts else "Question text unavailable"
            options = parts[1:] if len(parts) > 1 else []

            # Assume the first option is the correct answer for demonstration
            correct_answer = options[0] if options else ""

            quiz_questions.append({
                "question": q_text,
                "options": options,
                "correct_answer": correct_answer  # Add correct answer to the object
            })

        return jsonify({"questions": quiz_questions})

    except Exception as e:
        print("Error details:", e)
        return jsonify({"error": "An error occurred while generating the quiz. Please try again later."}), 500
# Handles checking the answer
@app.route("/check_answer", methods=["POST"])
def check_answer():
    data = request.json
    user_answer = data.get("answer", "")
    correct_answer = data.get("correct_answer", "")

    if user_answer == correct_answer:
        return jsonify({"result": "Correct!"}), 200
    else:
        return jsonify({"result": "Incorrect, try again!"}), 200



if __name__ == "__main__":
    app.run(debug=True)
