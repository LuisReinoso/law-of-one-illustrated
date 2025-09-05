#!/usr/bin/env python3
"""
MCP Tool Server for Nano-Banana Image Generation and Story Management

Usage: python nano_banana_mcp.py
"""
import json
import os
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from mcp.server.fastmcp import FastMCP
import fal_client
from reportlab.lib.pagesizes import letter, landscape, portrait
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import requests
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("nano_banana_tools")

# Configure fal_client
FAL_KEY = os.environ.get("FAL_KEY")
if not FAL_KEY:
    logger.warning("FAL_KEY environment variable not set - image generation will fail")


def _download_and_validate_image(image_url: str) -> Optional[bytes]:
    """Download and validate image from URL"""
    try:
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Validate it's an image
        img = Image.open(BytesIO(response.content))
        img.verify()
        
        return response.content
    except Exception as e:
        logger.error(f"Failed to download/validate image from {image_url}: {e}")
        return None



@mcp.tool()
def generate_image(prompt: str, local_path: str, num_images: int = 1, output_format: str = "jpeg") -> Dict[str, Any]:
    """
    Generate images using Nano-Banana Text-to-Image and save locally.
    
    Args:
        prompt: Text description for image generation (max 5000 chars)
        local_path: Local file path to save image (e.g., 'stories/title/images/style_reference.jpeg')
        num_images: Number of images to generate (1-4)
        output_format: Output format ("jpeg" or "png")
        
    Returns:
        Dictionary with generated images metadata and local path
    """
    try:
        # Input validation
        if len(prompt) > 5000:
            raise ValueError("Prompt exceeds maximum length of 5000 characters")
        if not 1 <= num_images <= 4:
            raise ValueError("num_images must be between 1 and 4")
        if output_format not in ["jpeg", "png"]:
            raise ValueError("output_format must be 'jpeg' or 'png'")
        
        # Call Nano-Banana T2I
        result = fal_client.run("fal-ai/nano-banana", arguments={
            "prompt": prompt,
            "num_images": num_images,
            "output_format": output_format,
            "sync_mode": False
        })
        
        # Get the generated image URL
        if not result.get("images"):
            raise Exception("No images generated")
        
        image_url = result["images"][0]["url"]  # Use first generated image
        
        # Download and save locally (REQUIRED)
        img_data = _download_and_validate_image(image_url)
        if not img_data:
            raise Exception(f"Failed to download generated image from {image_url}")
        
        # Create parent directories if needed
        local_path_obj = Path(local_path)
        local_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to specified path
        local_path_obj.write_bytes(img_data)
        
        return {
            "url": image_url,
            "local_path": str(local_path),
            "prompt": prompt,
            "model": "nano-banana",
            "mode": "text-to-image",
            "size_bytes": len(img_data),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        return {
            "error": str(e),
            "images": [],
            "prompt": prompt,
            "timestamp": datetime.now().isoformat()
        }


@mcp.tool()
def edit_image(prompt: str, image_urls: List[str], local_path: str, num_images: int = 1, output_format: str = "jpeg") -> Dict[str, Any]:
    """
    Edit/fuse multiple images using Nano-Banana Image-to-Image and save locally.
    
    Args:
        prompt: Text description for image editing
        image_urls: List of input image URLs (max 10)
        local_path: Local file path to save image (e.g., 'stories/title/images/page_01.jpeg')
        num_images: Number of output images (1-4) 
        output_format: Output format ("jpeg" or "png")
        
    Returns:
        Dictionary with edited images metadata and local path
    """
    try:
        # Input validation
        if len(prompt) > 5000:
            raise ValueError("Prompt exceeds maximum length of 5000 characters")
        if not image_urls:
            raise ValueError("At least one image_url is required")
        if len(image_urls) > 10:
            raise ValueError("Maximum 10 image URLs allowed")
        if not 1 <= num_images <= 4:
            raise ValueError("num_images must be between 1 and 4")
        if output_format not in ["jpeg", "png"]:
            raise ValueError("output_format must be 'jpeg' or 'png'")
        
        # Call Nano-Banana I2I Edit
        result = fal_client.run("fal-ai/nano-banana/edit", arguments={
            "prompt": prompt,
            "image_urls": image_urls,
            "num_images": num_images,
            "output_format": output_format,
            "sync_mode": False
        })
        
        # Get the edited image URL
        if not result.get("images"):
            raise Exception("No images generated")
        
        image_url = result["images"][0]["url"]  # Use first generated image
        
        # Download and save locally (REQUIRED)
        img_data = _download_and_validate_image(image_url)
        if not img_data:
            raise Exception(f"Failed to download edited image from {image_url}")
        
        # Create parent directories if needed
        local_path_obj = Path(local_path)
        local_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to specified path
        local_path_obj.write_bytes(img_data)
        
        return {
            "url": image_url,
            "local_path": str(local_path),
            "prompt": prompt,
            "input_image_urls": image_urls,
            "model": "nano-banana",
            "mode": "image-to-image",
            "size_bytes": len(img_data),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Image editing failed: {e}")
        return {
            "error": str(e),
            "images": [],
            "prompt": prompt,
            "input_image_urls": image_urls,
            "timestamp": datetime.now().isoformat()
        }


@mcp.tool()
def save_story(story_data: Dict[str, Any], local_path: str) -> Dict[str, Any]:
    """
    Save story data to specified file path.
    
    Args:
        story_data: Complete story data dictionary
        local_path: Exact file path to save JSON (e.g., 'stories/title/story_data.json')
        
    Returns:
        Dictionary with file path and metadata
    """
    try:
        # Add metadata
        story_data["saved_at"] = datetime.now().isoformat()
        story_data["version"] = "1.0"
        
        # Create parent directories if needed
        local_path_obj = Path(local_path)
        local_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to exact path specified
        with open(local_path_obj, "w", encoding="utf-8") as f:
            json.dump(story_data, f, ensure_ascii=False, indent=2)
        
        return {
            "file_path": str(local_path_obj),
            "story_directory": str(local_path_obj.parent),
            "title": story_data.get("title", "Untitled"),
            "pages": len(story_data.get("pages", [])),
            "size_bytes": local_path_obj.stat().st_size,
            "saved_at": story_data["saved_at"]
        }
        
    except Exception as e:
        logger.error(f"Failed to save story: {e}")
        return {
            "error": str(e),
            "file_path": None
        }


@mcp.tool()
def create_pdf(pages: List[Dict[str, Any]], local_path: str, orientation: str = "portrait") -> Dict[str, Any]:
    """
    Create a PDF from story pages and save to specified path.
    
    Args:
        pages: List of page dictionaries with 'text' and 'image_url'
        local_path: Exact file path to save PDF (e.g., 'stories/title/storybook.pdf')
        orientation: "portrait" or "landscape"
        
    Returns:
        Dictionary with PDF path and metadata
    """
    try:
        if not pages:
            raise ValueError("At least one page is required")
        
        # Create parent directories if needed
        pdf_path_obj = Path(local_path)
        pdf_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        pdf_path = pdf_path_obj
        
        # Set page size
        pagesize = portrait(letter) if orientation == "portrait" else landscape(letter)
        width, height = pagesize
        
        # Create PDF
        c = canvas.Canvas(str(pdf_path), pagesize=pagesize)
        margin = 0.8 * inch
        
        # Calculate layout dimensions
        if orientation == "portrait":
            img_h = height * 0.60  # 60% of page for image
            img_w = width - 2 * margin
            text_y_start = height - margin - img_h - 0.4 * inch
        else:
            img_h = height * 0.70  # 70% of page for image
            img_w = (width - 3 * margin) * 0.6  # 60% of width for image
            text_x_start = img_w + 2 * margin
            text_y_start = height - margin - 0.4 * inch
        
        for i, page in enumerate(pages, 1):
            # Draw image if available
            image_url = page.get("image_url")
            if image_url:
                try:
                    img_data = _download_and_validate_image(image_url)
                    if img_data:
                        img_reader = ImageReader(BytesIO(img_data))
                        c.drawImage(
                            img_reader, 
                            margin, 
                            height - margin - img_h,
                            img_w, 
                            img_h, 
                            preserveAspectRatio=True, 
                            anchor='n'
                        )
                except Exception as e:
                    logger.warning(f"Failed to add image to page {i}: {e}")
            
            # Draw text (optional - title pages may have no text)
            text = page.get("text", "")
            if text:
                c.setFont("Times-Roman", 12)
                
                # Split text into lines
                words = text.split()
                lines = []
                current_line = []
                max_width = (width - 2 * margin) if orientation == "portrait" else (width - text_x_start - margin)
                max_chars_per_line = int(max_width / 7)  # Approximate character width
                
                for word in words:
                    if len(" ".join(current_line + [word])) <= max_chars_per_line:
                        current_line.append(word)
                    else:
                        if current_line:
                            lines.append(" ".join(current_line))
                            current_line = [word]
                        else:
                            lines.append(word)  # Single long word
                
                if current_line:
                    lines.append(" ".join(current_line))
                
                # Draw text lines
                x = margin if orientation == "portrait" else text_x_start
                y = text_y_start
                line_height = 14
                
                for line in lines:
                    if y > margin:  # Don't draw below margin
                        c.drawString(x, y, line)
                        y -= line_height
            
            # Add page number
            c.setFont("Times-Roman", 10)
            c.drawString(width - margin - 30, margin - 10, f"Page {i}")
            
            c.showPage()
        
        # Finalize PDF
        c.save()
        
        return {
            "pdf_path": str(pdf_path),
            "filename": pdf_path.name,
            "pages": len(pages),
            "orientation": orientation,
            "size_bytes": pdf_path.stat().st_size,
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"PDF creation failed: {e}")
        return {
            "error": str(e),
            "pdf_path": None
        }


if __name__ == "__main__":
    import sys
    # Run MCP server
    if len(sys.argv) > 1 and sys.argv[1] == "stdio":
        mcp.run()
    else:
        mcp.run()
