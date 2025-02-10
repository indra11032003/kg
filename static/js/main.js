function askQuestion() {
    const question = document.getElementById("question").value;
    const context = document.getElementById("summary").innerText;

    fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, context }),
    })
        .then((response) => response.json())
        .then((data) => {
            document.getElementById("answer").innerText = data.answer;
        });
}