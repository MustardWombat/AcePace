async function generateQuiz() {
    console.log("Generate button clicked");

    // Get class material text directly from textarea
    const classMaterial = document.getElementById("classMaterial").value;

    // Send the class material to the Flask backend
    const quizResponse = await fetch("/generate_quiz", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: classMaterial }),
    });

    const quiz = await quizResponse.json();
    displayQuiz(quiz.questions);
}

let quizQuestions = []; // Declare globally to access in submitAnswer
let currentQuestionIndex = 0;

function displayQuiz(questions) {
    quizQuestions = questions; // Store the questions globally
    const quizDiv = document.getElementById("quiz");
    quizDiv.innerHTML = "";

    const question = questions[currentQuestionIndex];
    const questionDiv = document.createElement("div");
    questionDiv.classList.add("question");

    const questionText = document.createElement("p");
    questionText.textContent = `${currentQuestionIndex + 1}. ${question.question}`;
    questionDiv.appendChild(questionText);

    question.options.forEach((option) => {
        const optionLabel = document.createElement("label");
        const optionInput = document.createElement("input");
        optionInput.type = "radio";
        optionInput.name = `question-${currentQuestionIndex}`;
        optionInput.value = option;

        optionLabel.appendChild(optionInput);
        optionLabel.append(option);
        questionDiv.appendChild(optionLabel);
        questionDiv.appendChild(document.createElement("br"));
    });

    quizDiv.appendChild(questionDiv);
}

function submitAnswer() {
    const options = document.getElementsByName(`question-${currentQuestionIndex}`);
    let selectedOption = "";

    for (const option of options) {
        if (option.checked) {
            selectedOption = option.value;
            break;
        }
    }

    // Check if selectedOption is empty
    if (!selectedOption) {
        alert("Please select an option.");
        return; // Stop the function if no option is selected
    }

    const correctAnswer = quizQuestions[currentQuestionIndex].correct_answer;

    fetch("/check_answer", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ answer: selectedOption, correct_answer: correctAnswer })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.result); // Show result to the user
        // Optionally proceed to the next question here
        currentQuestionIndex++;
        if (currentQuestionIndex < quizQuestions.length) {
            displayQuiz(quizQuestions); // Display the next question
        } else {
            alert("Quiz completed!");
        }
    })
    .catch(error => console.error("Error:", error));
}
