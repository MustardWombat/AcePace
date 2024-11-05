function submitAnswer(answer, button) {
    fetch("/submit_answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer: answer })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("feedback").innerText = data.result;

        // Change button color based on result
        if (data.result === "Correct!") {
            button.style.backgroundColor = "green";
        } else {
            button.style.backgroundColor = "red";
        }

        // Disable all option buttons after selection
        const optionButtons = document.querySelectorAll("#options button");
        optionButtons.forEach(btn => btn.disabled = true);

        // Update score summary right after answering
        updateScoreSummary();

        // Load the next question after a delay to give feedback time
        setTimeout(() => {
            loadNextQuestion();
        }, 1500);  // 1.5-second delay
    });
}
