
// Wait for the DOM to fully load before running the script
document.addEventListener("DOMContentLoaded", function() {
    
    // Get references to key DOM elements
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const chatBox = document.getElementById("chatbox");

    // Function to append a message to the chat box
    function appendMessage(sender, text) {
        // Create the message container div
        const messageDiv = document.createElement("div");
        
        // Add the appropriate class based on the sender ('user-message' or 'bot-message')
        messageDiv.classList.add(sender === "User" ? "user-message" : "bot-message");
        
        // Set the content of the message
        const messageContent = document.createElement("p");
        messageContent.textContent = text;
        
        messageDiv.appendChild(messageContent);
        chatBox.appendChild(messageDiv);
        
        // Auto-scroll to the bottom of the chat box
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Handle form submission
    chatForm.addEventListener("submit", function(event) {
        event.preventDefault(); // Prevent page reload

        const userText = userInput.value.trim();

        // Do nothing if input is empty
        if (!userText) return;

        // 1. Display User's Message
        appendMessage("User", userText);

        // Clear the input field
        userInput.value = "";

        // 2. Send Message to Backend (Flask)
        // Using the native Fetch API
        fetch(`/get?msg=${encodeURIComponent(userText)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.text(); // Flask returns plain text
            })
            .then(botResponse => {
                // 3. Display Bot's Response
                // Add a small delay to simulate "thinking" (optional but nice UI touch)
                setTimeout(() => {
                    appendMessage("Bot", botResponse);
                }, 500);
            })
            .catch(error => {
                console.error("Error fetching chatbot response:", error);
                appendMessage("Bot", "Sorry, I am having trouble connecting to the server.");
            });
    });
});
