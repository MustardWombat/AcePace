from flask import Flask, request, jsonify, render_template, session
import openai
import os
from dotenv import load_dotenv
import csv
import fitz  # PyMuPDF for PDF handling
import pytesseract  # Tesseract OCR
from PIL import Image  # For handling image conversions

# Load environment variables from Key.env
load_dotenv("Key.env")

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed to keep track of question index

# Access the OpenAI API key from the environment
openai.api_key = os.getenv("OPENAI_API_KEY")


# Function to read PDF content with OCR support
def pdf_reader(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as pdf:
            for page_num in range(len(pdf)):
                page = pdf[page_num]
                page_text = page.get_text("text")

                if page_text.strip():  # If there's text, use it
                    text += page_text
                else:
                    # If no text is detected, render the page as an image and use OCR
                    pix = page.get_pixmap()  # Render page to an image
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    page_text = pytesseract.image_to_string(img)  # Use OCR to extract text
                    text += page_text

        return text
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return None


# Calculate final score and current streak
def calculate_final_score():
    total_score = 0
    current_streak = 0
    max_streak = 0

    try:
        with open("user_scores.csv", mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header

            for row in reader:
                result = row[3]  # Assume the result is in the fourth column (Correct! or Incorrect)

                if result == "Correct!":
                    current_streak += 1
                    total_score += 10  # Increment score by 10 points for each correct answer
                    max_streak = max(max_streak, current_streak)
                else:
                    current_streak = 0  # Reset streak on an incorrect answer
    except FileNotFoundError:
        print("user_scores.csv not found. Starting with default score values.")
        total_score = 0
        max_streak = 0

    return {"Total Score": total_score, "Current Streak": current_streak, "Max Streak": max_streak}


# Generate the full quiz and save it in the session
@app.route("/generate_quiz", methods=["POST"])
def generate_quiz():
    class_material = ""

    # Check for PDF file
    pdf_file = request.files.get("pdf")
    if pdf_file:
        pdf_path = os.path.join("uploads", pdf_file.filename)
        pdf_file.save(pdf_path)
        pdf_text = pdf_reader(pdf_path)
        if not pdf_text:
            return jsonify({"error": "Failed to read the PDF file."}), 400
        class_material += pdf_text  # Append PDF text to class_material

    # Get text input
    text_input = request.form.get("text", "")
    if text_input:
        class_material += "\n" + text_input  # Append text input to class_material

    if not class_material.strip():
        return jsonify({"error": "No class material provided"}), 400

    # OpenAI prompt for generating quiz questions
    prompt = f"""
    Create a quiz based on the following material. Each question should be a well-structured multiple-choice question with one correct answer and three plausible, factually incorrect options. Ensure the questions are challenging yet clear.
    I want the questions to have a difficulty of 10 out of 10, with 10 being insanely hard, while 1 being easy
    Material:
    {class_material}

    Please format the output as:
    Q1. [Question here]
    A) Option 1
    B) Option 2
    C) Option 3
    D) Option 4
    Correct Answer: [Correct Answer Letter]
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response['choices'][0]['message']['content']
        questions = response_text.strip().split("\n\n")
        quiz_questions = []

        for idx, question in enumerate(questions):
            parts = question.strip().split("\n")
            q_text = parts[0] if parts else "Question text unavailable"
            options = [option[3:].strip() for option in parts[1:5] if
                       len(option) > 3]  # Extract options after "A) ", "B) ", etc.

            # Safely extract and validate the correct answer letter
            correct_letter = ""
            for part in parts:
                if "Correct Answer:" in part:
                    correct_letter = part.split("Correct Answer:")[-1].strip()
                    break

            if len(correct_letter) == 1 and correct_letter in "ABCD":
                correct_answer_index = ord(correct_letter) - ord('A')
                if 0 <= correct_answer_index < len(options):
                    correct_answer = options[correct_answer_index]
                else:
                    correct_answer = options[0]  # Default to first option if index is out of range
            else:
                correct_answer = options[0]  # Default to first option if correct_letter is invalid

            quiz_questions.append({
                "question_id": idx + 1,
                "question": q_text,
                "options": options,
                "correct_answer": correct_answer
            })

        # Save questions in session and reset the current question index
        session['quiz_questions'] = quiz_questions
        session['current_question_index'] = 0
        print("Quiz generated and stored in session.")  # Debugging

        return jsonify({"message": "Quiz generated successfully"}), 200

    except Exception as e:
        print("Error during quiz generation:", e)
        return jsonify({"error": "An error occurred while generating the quiz. Please try again later."}), 500


# Serve one question at a time
@app.route("/get_question", methods=["GET"])
def get_question():
    quiz_questions = session.get('quiz_questions', [])
    current_index = session.get('current_question_index', 0)

    if not quiz_questions:
        return jsonify({"error": "No quiz available. Please generate the quiz first."}), 400

    if current_index < len(quiz_questions):
        question = quiz_questions[current_index]
        return jsonify({"question": question})
    else:
        # Reset the question index to start the quiz over
        session['current_question_index'] = 0
        question = quiz_questions[0]  # Start with the first question again
        return jsonify({"question": question, "message": "Quiz restarted"})


# Update the question index after an answer is submitted
@app.route("/submit_answer", methods=["POST"])
def submit_answer():
    data = request.json
    user_answer = data.get("answer", "")
    current_index = session.get('current_question_index', 0)

    quiz_questions = session.get('quiz_questions', [])
    if current_index < len(quiz_questions):
        correct_answer = quiz_questions[current_index]["correct_answer"]
        result = "Correct!" if user_answer.strip().lower() == correct_answer.strip().lower() else "Incorrect, try again!"

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
    # Ensure the uploads directory exists
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
