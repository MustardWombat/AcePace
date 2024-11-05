# Quiz Generation and Scoring App

A Flask web application that generates multiple-choice quizzes based on provided class material. The app uses OpenAI's API to create questions, tracks answers, and calculates scores. Results and score streaks are stored in a CSV file for easy data handling.

## Features
- Generate a multiple-choice quiz from custom class material.
- Answer questions one at a time and receive feedback on correctness.
- Track scores and streaks across multiple sessions, saved in `user_scores.csv`.
- View a final score summary with total score, current streak, and max streak.

## Tech Stack
- **Python**: Core language for backend logic.
- **Flask**: Web framework for handling routes and user interactions.
- **OpenAI API**: Generates quiz questions and answers from provided material.
- **CSV**: Stores user answers and score data.
- **dotenv**: Manages environment variables for secure API keys.

## Requirements
- Python 3.8+
- [OpenAI API Key](https://beta.openai.com/signup/)
- Flask
- python-dotenv

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/quiz-generation-app.git
    cd quiz-generation-app
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set up environment variables**:
   - Create a file named `Key.env` in the project root.
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_openai_api_key
     ```

4. **Run the application**:
    ```bash
    python app.py
    ```

   - The app will start on `http://127.0.0.1:5000`.

## Endpoints

- **Generate Quiz** (`POST /generate_quiz`): Generates quiz questions based on provided class material. Requires JSON data:
  ```json
  { "text": "Class material goes here" }
