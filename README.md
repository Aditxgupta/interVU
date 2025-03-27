# interVU - AI Interview Practice Platform

A mini project developed by 6th year Electronic and Telecommunication Engineering students at Dayananda Sagar College of Engineering.

## Team Members
- Aditya Gupta
- Asadulla Ansari
- Priyanshu Sachan
- Gautam S

## Overview
interVU is an AI-powered interview practice platform that helps users improve their interview skills through interactive conversations. The platform uses advanced speech recognition and natural language processing to create a realistic interview experience.

## Features
- Real-time speech-to-text conversion using Replicate's Whisper model
- AI-powered interview responses using Google's Gemini model
- Text-to-speech capabilities for AI responses
- Dark/Light mode interface
- Interactive UI with real-time status updates
- Support for various interview topics and questions

## Prerequisites
- Python 3.8 or higher
- PyAudio
- Flask
- Replicate API token
- Google API key

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd mini_project_interVU
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Unix or MacOS
source .venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# On Windows PowerShell
$env:REPLICATE_API_TOKEN = "your_replicate_api_token"
$env:GOOGLE_API_KEY = "your_google_api_key"

# On Unix or MacOS
export REPLICATE_API_TOKEN="your_replicate_api_token"
export GOOGLE_API_KEY="your_google_api_key"
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Click on "Talk to Speak" to start an interview session
4. Speak clearly into your microphone when prompted
5. Listen to the AI interviewer's responses
6. Click "Stop Interview" when you're finished

## Project Structure
```
mini_project_interVU/
├── app.py                 # Flask application
├── audio_interface.py     # Audio handling and speech recognition
├── static/
│   ├── css/
│   │   └── styles.css    # Styling
│   └── js/
│       └── main.js       # Frontend functionality
└── templates/
    └── index.html        # Main application interface
```

## Technologies Used
- Python
- Flask
- PyAudio
- Replicate API (Whisper model)
- Google Gemini API
- HTML5
- CSS3
- JavaScript

## Contributing
This is a mini project developed for academic purposes. Contributions are welcome but please note this is primarily for learning and demonstration purposes.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Replicate for providing the Whisper model API
- Google for the Gemini model
- All contributors and testers who helped improve the project