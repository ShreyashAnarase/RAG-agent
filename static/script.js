    async function sendMessage() {
        let userInput = document.getElementById("userInput");
        let chatBox = document.getElementById("chatBox");

        if (userInput.value.trim() === "") return; // Ignore empty messages

        // Add user message to chat
        let userMessage = document.createElement("div");
        userMessage.className = "message-user";
        userMessage.innerText = userInput.value;
        chatBox.appendChild(userMessage);

        let userText = userInput.value;
        userInput.value = ""; // Clear input field

        // Send user input to FastAPI backend
        let response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userText })
        });
        console.log(response);
        let data = await response.json();
        console.log( "resp = ", data);

        // Add bot response to chat
        let botMessage = document.createElement("div");
        botMessage.className = "message-bot";
        botMessage.innerText = data[0];
        chatBox.appendChild(botMessage);
        const linebreak= document.createElement("br");
        chatBox.appendChild(linebreak);

        // Scroll chat to bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function handleKeyPress(event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    }

document.getElementById("fileInput").addEventListener("change", uploadFile);

    async function uploadFile(event) {
    const file = event.target.files[0];

    if (!file) {
        alert("Please select a file.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
        console.log(" Going to attempt uploading the file ");
        const response = await fetch("/upload-doc/", {
            method: "POST",
            body: formData
        });

        // const result = await response.json();
        // alert(" Uploaded: " + result.message);
        const text = await response.text();
        console.log("Raw response text:", text);
    } catch (error) {
        console.error("Upload failed:", error);
        alert("Upload failed.");
    }
}
