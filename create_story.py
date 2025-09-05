#!/usr/bin/env python3
"""
Story Creator with Proper MCP Integration

This script ensures the environment is properly set up for MCP integration
with the Claude Code SDK.

Usage:
  python create_story.py "brave fox discovers a hidden garden"
  python create_story.py --debug "space friends explore planets"
  python create_story.py --timeout 30 "dragon overcomes fear"
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from sdk_launcher import AutonomousStoryCreator

# Load environment variables from .env file
load_dotenv()

def setup_environment():
    """Set up the environment for proper MCP integration"""
    
    # 1. Ensure FAL_KEY is available
    fal_key = os.getenv("FAL_KEY")
    if not fal_key:
        print("❌ FAL_KEY not found in .env file")
        return False
    
    # 2. Unset ANTHROPIC_API_KEY to use Max plan (avoid credit issues)
    if "ANTHROPIC_API_KEY" in os.environ:
        del os.environ["ANTHROPIC_API_KEY"]
    
    # 3. Verify required files exist
    if not Path(".mcp.json").exists():
        print("❌ .mcp.json not found - copy from .mcp.json.template")
        return False
    
    if not Path("mcp_servers/nano_banana_mcp.py").exists():
        print("❌ MCP server not found")
        return False
    
    # 4. Ensure stories directory exists
    Path("stories").mkdir(parents=True, exist_ok=True)
    
    return True

def parse_args():
    """Parse command line arguments"""
    args = sys.argv[1:]
    debug_mode = False
    verbose_mode = False
    timeout_minutes = None
    topic_parts = []
    
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ['--debug', '-d']:
            debug_mode = True
            os.environ['DEBUG'] = '1'
        elif arg in ['--verbose', '-v']:
            verbose_mode = True
            os.environ['VERBOSE'] = '1'
        elif arg in ['--timeout', '-t']:
            if i + 1 < len(args):
                timeout_minutes = int(args[i + 1])
                os.environ['TIMEOUT_MINUTES'] = str(timeout_minutes)
                i += 1  # Skip next arg as it's the timeout value
            else:
                print("❌ --timeout requires a value in minutes")
                sys.exit(1)
        else:
            topic_parts.append(arg)
        i += 1
    
    # Set both debug and verbose if debug is enabled
    if debug_mode:
        os.environ['VERBOSE'] = '1'
    
    return debug_mode, verbose_mode, timeout_minutes, " ".join(topic_parts)

async def main():
    debug_mode, verbose_mode, timeout_minutes, topic = parse_args()
    
    if not topic:
        print("Claude Banana Agent")
        print("Usage: python create_story.py \"your story topic\"")
        print("\nExamples:")
        print("  python create_story.py \"robot discovers emotions\"")
        print("  python create_story.py \"fox and owl solve mysteries in watercolor style\"")  
        print("  python create_story.py \"space adventure, 10 pages\"")
        print("\nOptions: --debug --verbose --timeout 30")
        return
    
    print(f"Topic: {topic}")
    if debug_mode:
        print("Debug mode enabled")
    if timeout_minutes:
        print(f"Timeout: {timeout_minutes} minutes")
    
    # Set up environment
    if not setup_environment():
        return
    
    try:
        # Initialize creator
        creator = AutonomousStoryCreator()
        
        # Create the story
        result = await creator.create_story(topic)
        
        # Show results
        if result["success"]:
            # Find the story directory
            stories_path = Path("stories")
            if stories_path.exists():
                story_dirs = list(stories_path.glob("*"))
                if story_dirs:
                    latest_dir = max(story_dirs, key=lambda p: p.stat().st_mtime)
                    print(f"✓ Files saved to: {latest_dir}/")
        else:
            if "error" in result:
                print(f"❌ {result['error']}")
                if "No MCP tools were called" in result.get("error", ""):
                    print("Try: cp .mcp.json.template .mcp.json")
                
    except Exception as e:
        print(f"❌ Setup error: {e}")

if __name__ == "__main__":
    asyncio.run(main())