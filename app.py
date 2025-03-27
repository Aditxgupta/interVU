from flask import Flask, render_template, jsonify, request, Response
import os
import time
import json
from audio_interface import get_interview_manager

app = Flask(__name__)
interview_manager = get_interview_manager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-interview', methods=['POST'])
def start_interview():
    # Start the interview process
    result = interview_manager.start_interview()
    return jsonify(result)

@app.route('/stop-interview', methods=['POST'])
def stop_interview():
    # Stop the interview process
    result = interview_manager.stop_interview()
    return jsonify(result)

@app.route('/toggle-theme', methods=['POST'])
def toggle_theme():
    theme = request.json.get('theme', 'dark')
    # In a real app, you might save this to a user's session
    return jsonify({"status": "success", "theme": theme})

@app.route('/stream')
def stream():
    """Event stream for sending real-time updates to the client"""
    def generate():
        # Initial connection message
        yield f"data: {json.dumps({'event': 'connected'})}\n\n"
        
        # Keep connection open and check for new messages
        while True:
            # Check for new messages
            messages = interview_manager.get_messages() 
            if messages:
                for message in messages:
                    yield f"data: {json.dumps({'event': 'message', 'data': message})}\n\n"
            else:
                # Send heartbeat to keep connection alive
                yield f"data: {json.dumps({'event': 'heartbeat'})}\n\n"
            time.sleep(0.5)  # Check every 500ms
    
    return Response(generate(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True)