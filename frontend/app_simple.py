#!/usr/bin/env python3
"""
Dead Simple FastAPI Backend for Storybook Creation
One endpoint, one purpose: create stories!
"""

import os
import subprocess
import threading
import webbrowser
import time
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

class StoryRequest(BaseModel):
    topic: str

def run_story_generation(topic: str):
    """Run create_story.py in the parent directory"""
    try:
        parent_dir = Path(__file__).parent.parent
        print(f"🎨 Starting story generation: {topic}")
        
        # Set up environment with debug flags
        env = os.environ.copy()
        env['DEBUG'] = '1'
        env['VERBOSE'] = '1'
        
        # Run the story creation with uv - all output goes to terminal
        result = subprocess.run(
            ['uv', 'run', 'python', 'create_story.py', topic],
            cwd=parent_dir,
            capture_output=False,  # Let output stream to terminal
            text=True,
            env=env
        )
        
        if result.returncode == 0:
            print("✅ Story generation completed!")
        else:
            print("❌ Story generation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

@app.post("/create")
async def create_story(request: StoryRequest):
    """Create a story - runs in background"""
    print(f"📖 Received story request: {request.topic}")
    
    # Start generation in background thread
    thread = threading.Thread(target=run_story_generation, args=(request.topic,))
    thread.daemon = True
    thread.start()
    
    return {"message": "Story generation started!", "topic": request.topic}

@app.get("/")
async def get_index():
    """Serve the main page"""
    with open(Path(__file__).parent / "index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/gallery")
async def get_gallery():
    """Serve the gallery page"""
    with open(Path(__file__).parent / "gallery.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/frontend-background.png")
async def get_background():
    """Serve the background image"""
    from fastapi.responses import FileResponse
    return FileResponse(Path(__file__).parent / "frontend-background.png")

@app.get("/stories")
async def list_stories():
    """List all available stories"""
    import json
    stories_dir = Path(__file__).parent.parent / "stories"
    stories = []
    
    if stories_dir.exists():
        for story_folder in stories_dir.iterdir():
            if story_folder.is_dir() and not story_folder.name.startswith('.'):
                story_json = story_folder / "story_data.json"
                if story_json.exists():
                    try:
                        with open(story_json, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            stories.append({
                                "name": story_folder.name,
                                "title": data.get("title", story_folder.name),
                                "created": story_folder.stat().st_mtime
                            })
                    except:
                        pass
    
    # Sort by creation time, newest first
    stories.sort(key=lambda x: x["created"], reverse=True)
    return {"stories": stories}

@app.get("/stories/{story_name}/story_data.json")
async def get_story_data(story_name: str):
    """Get story data JSON"""
    import json
    story_file = Path(__file__).parent.parent / "stories" / story_name / "story_data.json"
    if story_file.exists():
        with open(story_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"error": "Story not found"}

@app.get("/stories/{story_name}/images/{filename}")
async def get_story_image(story_name: str, filename: str):
    """Serve story images"""
    from fastapi.responses import FileResponse
    image_file = Path(__file__).parent.parent / "stories" / story_name / "images" / filename
    if image_file.exists():
        return FileResponse(image_file)
    return {"error": "Image not found"}

def open_browser():
    """Open browser after a delay"""
    time.sleep(1.5)
    webbrowser.open('http://localhost:8080')

if __name__ == "__main__":
    import uvicorn
    
    print("🌟 Starting Storybook Creator...")
    print("📖 Opening browser at: http://localhost:8080")
    
    # Auto-open browser
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start server
    uvicorn.run(app, host="localhost", port=8080, log_level="error")