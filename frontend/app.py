#!/usr/bin/env python3
"""
Beautiful Storybook Creator Frontend
Ghibli-inspired web interface for generating illustrated stories
"""

import asyncio
import json
import os
import subprocess
import threading
import time
import webbrowser
from pathlib import Path
from queue import Queue, Empty
from flask import Flask, render_template_string, request, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Global state for story generation
generation_status = {
    'active': False,
    'progress': 0,
    'status': 'Ready',
    'story_path': None,
    'log_queue': Queue()
}

def run_story_generation(topic):
    """Run create_story.py and capture output"""
    try:
        # Change to parent directory to run create_story.py
        parent_dir = Path(__file__).parent.parent
        
        # Run the story creation process
        process = subprocess.Popen(
            ['python', 'create_story.py', topic],
            cwd=parent_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Stream output to queue and print to console
        for line in process.stdout:
            line = line.strip()
            if line:
                print(f"[STORY GEN] {line}")  # Keep terminal output visible
                generation_status['log_queue'].put(line)
                
                # Update progress based on output
                if "Topic:" in line:
                    generation_status['status'] = "Starting story creation..."
                    generation_status['progress'] = 10
                elif "Creating story:" in line:
                    generation_status['status'] = "Planning story structure..."
                    generation_status['progress'] = 20
                elif "TodoWrite" in line or "Creating characters" in line:
                    generation_status['status'] = "Designing characters..."
                    generation_status['progress'] = 30
                elif "generate_image" in line or "Generating" in line:
                    generation_status['status'] = "Painting illustrations..."
                    generation_status['progress'] = 60
                elif "create_pdf" in line or "PDF" in line:
                    generation_status['status'] = "Creating storybook..."
                    generation_status['progress'] = 90
                elif "Files saved to:" in line:
                    # Extract the story path
                    story_path = line.split("Files saved to: ")[-1].rstrip("/")
                    generation_status['story_path'] = story_path
                    generation_status['status'] = "Story complete!"
                    generation_status['progress'] = 100
        
        process.wait()
        
        if process.returncode == 0:
            generation_status['status'] = "Story ready to view!"
        else:
            generation_status['status'] = "Story generation failed"
            generation_status['progress'] = -1
            
    except Exception as e:
        print(f"[ERROR] Story generation failed: {e}")
        generation_status['status'] = f"Error: {e}"
        generation_status['progress'] = -1
    finally:
        generation_status['active'] = False

@app.route('/')
def index():
    """Serve the beautiful storybook interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate_story():
    """Start story generation"""
    if generation_status['active']:
        return jsonify({'error': 'Story generation already in progress'}), 400
    
    data = request.get_json()
    topic = data.get('topic', '').strip()
    
    if not topic:
        return jsonify({'error': 'Please provide a story topic'}), 400
    
    # Reset status
    generation_status.update({
        'active': True,
        'progress': 0,
        'status': 'Initializing...',
        'story_path': None,
        'log_queue': Queue()
    })
    
    # Start generation in background thread
    thread = threading.Thread(target=run_story_generation, args=(topic,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': 'Story generation started'})

@app.route('/status')
def get_status():
    """Get current generation status"""
    return jsonify({
        'active': generation_status['active'],
        'progress': generation_status['progress'],
        'status': generation_status['status'],
        'story_path': generation_status['story_path']
    })

@app.route('/logs')
def stream_logs():
    """Stream logs via Server-Sent Events"""
    def generate():
        while generation_status['active']:
            try:
                log = generation_status['log_queue'].get(timeout=1)
                yield f"data: {json.dumps({'log': log})}\n\n"
            except Empty:
                yield f"data: {json.dumps({'heartbeat': True})}\n\n"
        
        # Send final status
        yield f"data: {json.dumps({'complete': True})}\n\n"
    
    return Response(generate(), content_type='text/plain')

@app.route('/story/<path:filename>')
def serve_story_file(filename):
    """Serve story files"""
    try:
        parent_dir = Path(__file__).parent.parent
        file_path = parent_dir / filename
        
        if file_path.exists() and file_path.is_file():
            if filename.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return jsonify(json.load(f))
            else:
                # For images and other files
                from flask import send_file
                return send_file(file_path)
        else:
            return jsonify({'error': 'File not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# The beautiful HTML template will be defined here
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>✨ Storybook Creator</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/page-flip@2.0.7/dist/css/page-flip.css">
    <script src="https://cdn.jsdelivr.net/npm/page-flip@2.0.7/dist/js/page-flip.browser.js"></script>
    <style>
        /* Beautiful Ghibli-inspired styles will be added here */
    </style>
</head>
<body>
    <!-- Beautiful interface will be implemented here -->
    <div id="app">Loading...</div>
    
    <script>
        // JavaScript application will be implemented here
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🌟 Starting Beautiful Storybook Creator...")
    print("📖 Open your browser to: http://localhost:5000")
    
    # Auto-open browser after a short delay
    def open_browser():
        time.sleep(1.5)
        webbrowser.open('http://localhost:5000')
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    app.run(host='localhost', port=5000, debug=False)