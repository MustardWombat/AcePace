function generateQuiz() {
    const classMaterial = document.getElementById("classMaterial").value;

    fetch("/generate_quiz", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: classMaterial })
    })
    .then(response => response.json())
    .then(data => {
        const quizContainer = document.getElementById("quiz-container");
        quizContainer.innerHTML = "";

        data.questions.forEach((q, index) => {
            const questionDiv = document.createElement("div");
            questionDiv.className = "question";

            questionDiv.innerHTML = `<p>${q.question}</p>`;
            q.options.forEach(option => {
                const optionElem = document.createElement("button");
                optionElem.textContent = option;
                optionElem.onclick = () => submitAnswer(q.question_id, option, q.correct_answer);
                questionDiv.appendChild(optionElem);
            });

            quizContainer.appendChild(questionDiv);
        });
    });
}

function submitAnswer(question_id, answer, correct_answer) {
    fetch("/check_answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question_id, answer, correct_answer })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.result);
    });
}
