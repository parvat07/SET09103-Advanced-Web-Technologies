const socket = io();

document.getElementById('messageForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value;
    
    socket.emit('message', { msg: message });
    messageInput.value = '';
});

socket.on('message', function(data) {
    const messages = document.getElementById('messages');
    const messageItem = document.createElement('li');
    messageItem.textContent = data.msg; // Display the message
    messages.appendChild(messageItem); // Append the message to the list
});

document.addEventListener("DOMContentLoaded", function() {
    // Update date-time
    setInterval(() => {
        const now = new Date();
        document.getElementById("date-time").textContent = now.toLocaleString();
    }, 1000);

    // Fetch weather (use a placeholder or a real API)
    document.getElementById("weather").textContent = "Sunny, 25°C"; // Replace with API call
});
