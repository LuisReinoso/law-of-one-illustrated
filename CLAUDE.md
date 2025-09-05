# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Storybook Agent system that creates professional, illustrated children's storybooks using Claude Code SDK, MCP tools, and Fal Nano-Banana image generation. The system generates consistent, coherent storybooks with text, images, and PDF export capabilities.

## Architecture

### Core Components

1. **Agent Orchestration** (`agents/story_agent.py`): Claude Code SDK client that orchestrates the entire storybook creation process
2. **MCP Tool Server** (`mcp/storybook_tools_mcp.py`): Provides custom tools for image generation, PDF creation, and story persistence
3. **FastAPI Backend** (`app/main.py`): HTTP API endpoint for story creation requests
4. **React Viewer** (`frontend/`): Web-based storybook viewer with page navigation and PDF download

### Data Flow

1. User submits story brief → FastAPI endpoint
2. Story agent processes brief through 7-step workflow:
   - Intake: Parse user requirements
   - Plan: Create story outline and art style
   - Write: Generate page text and scenes
   - Style Lock: Create consistent art style and character plates
   - ArtSpec: Generate detailed art direction per page
   - Render: Generate images using Nano-Banana with multi-image references
   - QA & Export: Quality check and PDF generation

## Development Setup

### Backend Setup

```bash
# Python 3.10+ required
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with:
# ANTHROPIC_API_KEY=...
# FAL_KEY=...
# CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

### Running the System

```bash
# Test MCP server standalone
python mcp/storybook_tools_mcp.py stdio

# Run FastAPI backend
uvicorn app.main:app --reload

# Run frontend (separate terminal)
cd frontend
npm install
npm run dev
```

### Frontend Development

```bash
cd frontend
npm run dev      # Development server
npm run build    # Production build  
npm run preview  # Preview production build
```

## Key Development Patterns

### MCP Tool Integration

All image generation and file operations go through MCP tools:
- `nano_banana()`: Text-to-image and image-to-image editing with multi-image references
- `record_story()`: Persist story JSON to disk
- `layout_pdf()`: Generate printable PDF from story pages

### Consistency Mechanisms

- **Global Art Style**: Single style keyplate used as reference for all pages
- **Character Plates**: Generated once, reused across all pages featuring that character
- **Multi-image References**: Each page render includes style + character plates + previous page for continuity
- **QA Loop**: Automated quality checks for palette/wardrobe drift with targeted re-rendering

### Story Data Model

Stories follow a strict JSON schema with:
- Project metadata (title, audience, theme, art_style)
- Character definitions with visual tags
- Page array with text, scene descriptions, art specs, and rendered images
- Global style and character plate URLs

## File Structure (When Built)

```
storybook-agent/
├── plan.md                     # Project specification
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── app/main.py                # FastAPI application
├── agents/
│   ├── story_agent.py         # Main agent orchestrator
│   └── system_prompt.txt      # Agent system prompt
├── mcp/storybook_tools_mcp.py # MCP tool server
├── runs/                      # Generated stories and PDFs
└── frontend/                  # React viewer application
    ├── package.json
    ├── src/viewer/App.tsx     # Main viewer component
    └── public/story.json      # Sample story data
```

## Testing Story Creation

```bash
# Example API call
curl -X POST http://localhost:8000/stories \
  -H 'Content-Type: application/json' \
  -d '{
        "prompt": "Title: Roshi and the Misty Cedars\nAudience: 6–8\nLength: 10 pages\nArt Style: watercolor, soft edges, pencil linework; palette: teal, amber, moss\nCamera: 35mm, shallow DOF; Format: landscape\nTheme: courage and friendship\nMain character: Roshi (orange fox, blue scarf)"
      }'
```

## Important Constraints

- Text limited to ≤120 words per page
- Images generated with consistent art style and palette across all pages
- Multi-image references maintain character and prop consistency
- PDF export supports both portrait and landscape orientations
- All generated content stored in `./runs/` directory

## External Dependencies

- **Claude Code SDK**: Agent orchestration and tool calling
- **Fal Nano-Banana**: Image generation (both T2I and I2I with multi-image support)
- **ReportLab**: PDF generation
- **FastAPI**: Web API framework
- **React + Vite**: Frontend viewer application