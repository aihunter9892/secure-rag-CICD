/* =========================================
   BACKEND CONFIG
   ========================================= */

// Automatically switch between local and production
const BACKEND_URL = "/ask"
const textarea = document.getElementById("question");
const messagesDiv = document.getElementById("messages");


/* =========================================
   ENTER TO SEND (Shift+Enter = New Line)
   ========================================= */
textarea.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        askQuestion();
    }
});


/* =========================================
   NEW CHAT
   ========================================= */
function newChat() {
    messagesDiv.innerHTML = `
        <div class="message assistant">
            Hello! I’m your Tata Harrier assistant. Ask me anything about the vehicle.
        </div>
    `;
}


/* =========================================
   MAIN ASK FUNCTION (Streaming)
   ========================================= */
async function askQuestion() {
    const question = textarea.value.trim();
    if (!question) return;

    // Add user message
    addMessage(question, "user");
    textarea.value = "";

    // Create assistant message container
    const botMessage = addMessage("Thinking...", "assistant");

    try {
        const response = await fetch(BACKEND_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question })
        });

        if (!response.ok) {
            botMessage.innerText = "Server error. Please try again.";
            return;
        }

        if (!response.body) {
            botMessage.innerText = "Error: No response body.";
            return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        let fullResponse = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            fullResponse += chunk;

            // Render Markdown as rich text
            botMessage.innerHTML = marked.parse(fullResponse);

            // Auto-scroll
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

    } catch (error) {
        botMessage.innerText = "Error connecting to server.";
        console.error("Frontend error:", error);
    }
}


/* =========================================
   ADD MESSAGE TO CHAT
   ========================================= */
function addMessage(text, role) {
    const msg = document.createElement("div");
    msg.className = `message ${role}`;

    if (role === "assistant") {
        msg.innerHTML = marked.parse(text || "");
    } else {
        msg.textContent = text;
    }

    messagesDiv.appendChild(msg);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    return msg;
}