function fetchText() {
    fetch("/get-text")
        .then(response => response.json())
        .then(data => {
            const chatBox = document.getElementById("chat-box");
            const message = document.createElement("p");
            message.classList.add("message", "bot-message");
            message.innerText = data.text || "Error fetching text.";
            chatBox.appendChild(message);
            chatBox.scrollTop = chatBox.scrollHeight;
        })
        .catch(error => console.error("Error:", error));
}