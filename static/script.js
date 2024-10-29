async function generateQuiz() {
    console.log("Generate button clicked");

    // Get class material text directly from textarea
    const classMaterial = document.getElementById("classMaterial").value;

    // Now send the class material to the Flask backend
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

function displayQuiz(questions) {
    const quizDiv = document.getElementById("quiz");
    quizDiv.innerHTML = "";

    questions.forEach((question, index) => {
        const questionDiv = document.createElement("div");
        questionDiv.classList.add("question");

        const questionText = document.createElement("p");
        questionText.textContent = `${index + 1}. ${question.question}`;
        questionDiv.appendChild(questionText);

        question.options.forEach((option) => {
            const optionLabel = document.createElement("label");
            const optionInput = document.createElement("input");
            optionInput.type = "radio";
            optionInput.name = `question-${index}`;
            optionInput.value = option;

            optionLabel.appendChild(optionInput);
            optionLabel.append(option);
            questionDiv.appendChild(optionLabel);
            questionDiv.appendChild(document.createElement("br"));
        });

        quizDiv.appendChild(questionDiv);
    });
}
