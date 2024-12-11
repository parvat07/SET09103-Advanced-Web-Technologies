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
