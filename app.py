from flask import Flask, request, jsonify, render_template, session
import openai
import os
from dotenv import load_dotenv
import csv

# Load environment variables from key.env
load_dotenv("Key.env")

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed to keep track of question index

# Access the OpenAI API key from the environment
openai.api_key = os.getenv("OPENAI_API_KEY")


# Calculate final score with streaks and multipliers
def calculate_final_score(streak_criteria=3, base_score=10, multiplier_increment=0.5):
    total_score = 0
    streak_count = 0
    multiplier = 1

    try:
        with open("user_scores.csv", mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header

            for row in reader:
                result = row[3]  # Assume the result is in the fourth column (Correct! or Incorrect)

                if result == "Correct!":
                    streak_count += 1
                    total_score += int(base_score * multiplier)
                    if streak_count >= streak_criteria:
                        multiplier += multiplier_increment
                else:
                    streak_count = 0
                    multiplier = 1
    except FileNotFoundError:
        total_score = 0
        multiplier = 1

    return {"Total Score": total_score, "Final Multiplier": multiplier}


# Generate the full quiz and save it in the session
@app.route("/generate_quiz", methods=["POST"])
def generate_quiz():
    data = request.json
    class_material = data.get("text", "")
    if not class_material:
        return jsonify({"error": "No class material provided"}), 400

    prompt = f"Generate a quiz with multiple-choice questions from the following material:\n{class_material}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response['choices'][0]['message']['content']
        questions = response_text.strip().split("\n\n")
        quiz_questions = []

        for idx, question in enumerate(questions):
            parts = question.split("\n")
            q_text = parts[0] if parts else "Question text unavailable"
            options = parts[1:] if len(parts) > 1 else []
            correct_answer = options[0] if options else ""

            quiz_questions.append({
                "question_id": idx + 1,
                "question": q_text,
                "options": options,
                "correct_answer": correct_answer
            })

        session['quiz_questions'] = quiz_questions  # Save questions in session
        session['current_question_index'] = 0  # Start at the first question

        return jsonify({"message": "Quiz generated successfully"}), 200

    except Exception as e:
        print("Error during quiz generation:", e)
        return jsonify({"error": "An error occurred while generating the quiz. Please try again later."}), 500


# Serve one question at a time
@app.route("/get_question", methods=["GET"])
def get_question():
    quiz_questions = session.get('quiz_questions', [])
    current_index = session.get('current_question_index', 0)

    if current_index < len(quiz_questions):
        question = quiz_questions[current_index]
        return jsonify({"question": question})
    else:
        return jsonify({"message": "Quiz complete"}), 200


# Update the question index after an answer is submitted
@app.route("/submit_answer", methods=["POST"])
def submit_answer():
    data = request.json
    user_answer = data.get("answer", "")
    current_index = session.get('current_question_index', 0)

    quiz_questions = session.get('quiz_questions', [])
    if current_index < len(quiz_questions):
        correct_answer = quiz_questions[current_index]["correct_answer"]
        result = "Correct!" if user_answer == correct_answer else "Incorrect, try again!"

        # Append the result to the CSV file
        with open("user_scores.csv", mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([quiz_questions[current_index]["question_id"], user_answer, correct_answer, result])

        # Move to the next question
        session['current_question_index'] += 1
        return jsonify({"result": result})

    return jsonify({"message": "No more questions"}), 200


# Route to get the final score summary
@app.route("/get_score_summary", methods=["GET"])
def get_score_summary():
    score_data = calculate_final_score()
    return jsonify(score_data)


# Display main page
@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
