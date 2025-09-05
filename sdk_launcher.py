#!/usr/bin/env python3
"""
Autonomous Storybook Creation using Claude Code SDK

This script demonstrates how to create complete illustrated storybooks
programmatically using the Claude Code SDK with MCP image generation tools.

Based on learnings from manual runs documented in example_run.md
"""

import asyncio
import os
import json
import time
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AutonomousStoryCreator:
    """
    Autonomous storybook creation using Claude Code SDK with MCP tools
    """
    
    def __init__(self, fal_key: Optional[str] = None):
        self.fal_key = fal_key or os.getenv("FAL_KEY")
        if not self.fal_key:
            raise ValueError("FAL_KEY environment variable or parameter required")
        
        self.system_prompt = self._load_system_prompt()
        self.project_root = Path.cwd()
        
    def _load_system_prompt(self) -> str:
        """Load the enhanced system prompt"""
        prompt_path = Path("sdk_system_prompt.txt")
        if not prompt_path.exists():
            raise FileNotFoundError(f"System prompt file not found: {prompt_path}")
        
        return prompt_path.read_text(encoding="utf-8")
    
    def _verify_mcp_config(self) -> str:
        """Verify MCP configuration file exists and contains required server"""
        mcp_config_path = Path(".mcp.json")
        if not mcp_config_path.exists():
            raise FileNotFoundError("MCP configuration file .mcp.json not found")
        
        # Verify the MCP server file exists
        mcp_server_path = Path("mcp_servers/nano_banana_mcp.py")
        if not mcp_server_path.exists():
            raise FileNotFoundError(f"MCP server not found at {mcp_server_path}")
        
        return str(mcp_config_path.resolve())
    
    def _format_input(self, topic: str) -> str:
        """Format topic string into a clear prompt for the agent"""
        return f"""
CREATE COMPLETE STORYBOOK FROM THIS TOPIC:

{topic}

EXECUTE THE COMPLETE 7-STEP WORKFLOW AUTONOMOUSLY.
Extract all story elements from this input and expand into full storybook.
Begin with TodoWrite task creation and Step 0 - Intake.
"""
    
    async def create_story(self, topic: str) -> Dict[str, Any]:
        """
        Create a complete storybook from a topic string
        
        Args:
            topic: Simple topic description (e.g., "brave fox discovers hidden garden")
            
        Returns:
            Dictionary with creation results and file paths
        """
        # Format title for display
        title = topic[:50] + "..." if len(topic) > 50 else topic
        print(f"Creating story: '{title}'")
        
        # Ensure Max plan usage by temporarily unsetting API key
        original_api_key = os.environ.get("ANTHROPIC_API_KEY")
        if original_api_key:
            del os.environ["ANTHROPIC_API_KEY"]
        
        start_time = time.time()
        
        # Use file-based MCP config (let Claude CLI handle MCP server management)
        mcp_config_path = self._verify_mcp_config()
        
        # Configure SDK options
        options = ClaudeCodeOptions(
            system_prompt=self.system_prompt,
            allowed_tools=[
                "mcp__nano_banana_tools__generate_image",  # Now requires local_path 
                "mcp__nano_banana_tools__edit_image",      # Now requires local_path
                "mcp__nano_banana_tools__save_story",
                "mcp__nano_banana_tools__create_pdf",
                "TodoWrite"  # For progress tracking
            ],
            disallowed_tools=[
                "Read",
                "Grep", 
                "Task",
                "Write",
                "Glob",
                "Bash",  # No longer needed - images auto-save via MCP tools
            ],
            mcp_servers=mcp_config_path,  # Use file path instead of dict
            cwd=self.project_root,
            max_turns=100,  # Increased for complex story workflows
            max_thinking_tokens=10000,
            # Avoid interactive permission prompts that can stall headless runs
            permission_mode="bypassPermissions"
        )
        
        # Configuration complete
        
        try:
            result = {
                "success": False,
                "story_data": None,
                "files_created": {},
                "images_generated": [],
                "processing_time": 0,
                "full_response": ""
            }
            
            async with ClaudeSDKClient(options=options) as client:
                # Send the formatted topic
                formatted_input = self._format_input(topic)
                await client.query(formatted_input)
                
                # Stream and collect response with timeout
                print("Agent working...")
                response_text = ""
                tool_calls_detected = 0
                timeout_minutes = int(os.getenv('TIMEOUT_MINUTES', '20'))  # Default 20 minutes
                TIMEOUT_SECONDS = timeout_minutes * 60
                current_step = "Unknown"
                
                async for message in client.receive_response():
                    
                    # Check for timeout
                    if time.time() - start_time > TIMEOUT_SECONDS:
                        print(f"⏰ Timeout after {TIMEOUT_SECONDS}s - terminating")
                        break
                    
                    # Debug message type and structure
                    if os.getenv("DEBUG") and hasattr(message, 'content'):
                        print(f"🔧 {type(message).__name__}")
                    
                    if hasattr(message, 'content'):
                        for content_block in message.content:
                            # Log explicit tool use blocks for visibility
                            if hasattr(content_block, 'name') and hasattr(content_block, 'input') and hasattr(content_block, 'id'):
                                tool_calls_detected += 1
                                print(f"🛠️  {getattr(content_block, 'name', 'unknown').replace('mcp__nano_banana_tools__', '')}")
                                continue
                            # Log tool results
                            if hasattr(content_block, 'tool_use_id') and hasattr(content_block, 'content') and getattr(content_block, 'is_error', None) is not None:
                                if getattr(content_block, 'is_error', False):
                                    print("❌ Tool error")
                                continue
                            # Regular text chunks
                            if hasattr(content_block, 'text'):
                                chunk = content_block.text
                                response_text += chunk
                                # Track current step for progress
                                if '## STEP' in chunk:
                                    step_match = chunk.split('## STEP')[1][:20] if '## STEP' in chunk else ''
                                    current_step = step_match.split('-')[0].strip() if '-' in step_match else step_match.strip()
                                    print(f"📍 Step {current_step}")
                                # Print all output if VERBOSE env var is set
                                if os.getenv("VERBOSE"):
                                    print(chunk, end='', flush=True)
                
                elapsed_time = time.time() - start_time
                
                result["full_response"] = response_text
                result["processing_time"] = time.time() - start_time
                
                # Simple success detection
                timed_out = elapsed_time >= (TIMEOUT_SECONDS - 5)
                completed_all_steps = "STEP 7" in response_text or "COMPLETION" in response_text.upper()
                
                if timed_out:
                    print(f"⏰ Timed out after {int(elapsed_time/60)}m {int(elapsed_time%60)}s")
                    result["success"] = False
                    result["error"] = f"Timed out after {elapsed_time:.1f}s"
                elif tool_calls_detected == 0:
                    print("❌ No tools were called - check MCP configuration")
                    result["success"] = False
                    result["error"] = "Agent failed to call any MCP tools"
                elif completed_all_steps:
                    print(f"✓ Story complete in {int(elapsed_time/60)}m {int(elapsed_time%60)}s")
                    result["success"] = True
                else:
                    print(f"⚠️  Partially completed in {int(elapsed_time/60)}m {int(elapsed_time%60)}s")
                    result["success"] = False
                    result["error"] = "Workflow did not complete all steps"
                
                return result
                
        except Exception as e:
            print(f"❌ Error during story creation: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time,
                "full_response": ""
            }
        finally:
            # Restore original API key if it was set
            if original_api_key:
                os.environ["ANTHROPIC_API_KEY"] = original_api_key
    


# Example story topics for testing
EXAMPLE_TOPICS = [
    # Single character stories
    "brave fox discovers a hidden garden",
    "robot learns to paint beautiful pictures", 
    "mouse builds a flying machine",
    "dragon who's afraid of fire learns to be brave",
    "underwater princess saves the ocean",
    "owl becomes a night detective",
    
    # Multi-character stories (demonstrates automatic character extraction)
    "two space friends explore colorful planets",
    "three little bears discover goldilocks in their house",
    "cat and dog team up to find lost treasure",
    "brother and sister rescue a baby dragon",
    "group of forest animals build a treehouse together",
    "twin rabbits solve the mystery of the missing carrots"
]


async def main():
    """
    Example usage of the autonomous story creator with topic-based input
    """
    print("Claude Banana Agent Demo")
    print("=" * 30)
    
    try:
        creator = AutonomousStoryCreator()
    except Exception as e:
        print(f"Setup error: {e}")
        return
    
    # Demo topic
    topic = "two space friends explore colorful planets"
    print(f"Topic: '{topic}'")
    
    # Create the story
    result = await creator.create_story(topic)
    
    # Show final result only
    if not result["success"] and "error" in result:
        print(f"Error: {result['error']}")
    
    print(f"\nTry: python create_story.py 'your topic here'")


if __name__ == "__main__":
    # Check requirements
    if not os.getenv("FAL_KEY"):
        print("❌ FAL_KEY environment variable required")
        print("   Add your FAL API key to .env file:")
        print("   echo 'FAL_KEY=your_key_here' >> .env")
        print("   Or export directly: export FAL_KEY=your_key_here")
        exit(1)
    
    asyncio.run(main())
