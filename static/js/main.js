document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const body = document.body;
    const startInterviewBtn = document.getElementById('start-interview');
    const stopInterviewBtn = document.getElementById('stop-interview');
    const statusText = document.getElementById('status-text');
    const statusDot = document.getElementById('status-dot');
    const welcomeScreen = document.getElementById('welcome-screen');
    const interviewScreen = document.getElementById('interview-screen');
    const interviewMessages = document.getElementById('interview-messages');
    const newInterviewBtn = document.getElementById('new-interview');
    const optionCards = document.querySelectorAll('.option-card');
    const suggestionItems = document.querySelectorAll('.suggestion-item');
    
    // Event source for real-time updates
    let eventSource = null;
    const synth = window.speechSynthesis;
    
    // Theme toggle functionality
    themeToggleBtn.addEventListener('click', function() {
        document.body.classList.toggle('light-mode');
        const theme = document.body.classList.contains('light-mode') ? 'light' : 'dark';
        fetch('/toggle-theme', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ theme })
        });
    });
    
    // Check for saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        body.classList.remove('dark-mode');
        body.classList.add('light-mode');
    }
    
    // Start interview button
    startInterviewBtn.addEventListener('click', function() {
        switchToInterviewScreen();
        startInterview();
    });
    
    // Stop interview button
    stopInterviewBtn.addEventListener('click', function() {
        stopInterview();
    });
    
    // New interview button
    newInterviewBtn.addEventListener('click', function() {
        resetInterview();
    });
    
    // Option cards
    optionCards.forEach(card => {
        card.addEventListener('click', function() {
            switchToInterviewScreen();
            // Add initial message
            addMessage("Starting a new interview session...", 'system');
        });
    });
    
    // Suggestion items
    suggestionItems.forEach(item => {
        item.addEventListener('click', function() {
            switchToInterviewScreen();
            const question = item.textContent;
            startInterview(question);
        });
    });
    
    function setupEventSource() {
        if (eventSource) {
            eventSource.close();
        }
        
        eventSource = new EventSource('/stream');
        
        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            console.log('Server event:', data);
            
            if (data.event === 'connected') {
                console.log('Connected to server stream');
            } else if (data.event === 'message') {
                // Handle the message based on its type
                const message = data.data;
                addMessage(message.text, message.type);
            } else if (data.event === 'heartbeat') {
                // Ignore heartbeat events
                return;
            }
        };
        
        eventSource.onerror = function() {
            console.log('EventSource connection error. Reconnecting in 5 seconds...');
            eventSource.close();
            setTimeout(setupEventSource, 5000);
        };
    }
    
    function switchToInterviewScreen() {
        welcomeScreen.classList.add('hidden');
        interviewScreen.classList.remove('hidden');
    }
    
    function resetInterview() {
        interviewMessages.innerHTML = '';
        welcomeScreen.classList.remove('hidden');
        interviewScreen.classList.add('hidden');
        statusText.textContent = 'Ready';
        statusDot.classList.remove('active');
        startInterviewBtn.classList.remove('hidden');
        stopInterviewBtn.classList.add('hidden');
        
        // Close event source if open
        if (eventSource) {
            eventSource.close();
            eventSource = null;
        }
    }
    
    function startInterview(initialQuestion = null) {
        addMessage("Starting interview...", 'system');
        
        fetch('/start-interview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                initialQuestion: initialQuestion
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            statusText.textContent = 'Listening...';
            statusDot.classList.add('active');
            startInterviewBtn.classList.add('hidden');
            stopInterviewBtn.classList.remove('hidden');
            
            // Setup event source for real-time updates
            setupEventSource();
            
            // Add initial message explaining how to use the system
            addMessage("The interview has started. Speak clearly into your microphone to respond to the interviewer's questions. The AI will listen and respond. Click 'Stop' when you're finished.", 'system');
            
        })
        .catch((error) => {
            console.error('Error:', error);
            statusText.textContent = 'Error';
            addMessage("There was an error starting the interview. Please try again.", 'system');
        });
    }
    
    function stopInterview() {
        fetch('/stop-interview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            statusText.textContent = 'Ready';
            statusDot.classList.remove('active');
            startInterviewBtn.classList.remove('hidden');
            stopInterviewBtn.classList.add('hidden');
            
            // Close event source
            if (eventSource) {
                eventSource.close();
                eventSource = null;
            }
            
            addMessage("Interview session ended. Click 'Talk to Speak' to start a new session.", 'system');
        })
        .catch((error) => {
            console.error('Error:', error);
            addMessage("There was an error stopping the interview.", 'system');
        });
    }
    
    function addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        
        if (type === 'user') {
            messageDiv.classList.add('user-message');
        } else if (type === 'ai') {
            messageDiv.classList.add('ai-message');
        } else if (type === 'system') {
            messageDiv.classList.add('system-message');
        }
        
        messageDiv.textContent = text;
        interviewMessages.appendChild(messageDiv);
        interviewMessages.scrollTop = interviewMessages.scrollHeight;
    }
    
    // Add system-message class to CSS
    const style = document.createElement('style');
    style.textContent = `
        .system-message {
            background-color: #333;
            color: #ccc;
            margin: 10px auto;
            padding: 10px;
            border-radius: 8px;
            font-style: italic;
            text-align: center;
            max-width: 90%;
        }
    `;
    document.head.appendChild(style);
});
