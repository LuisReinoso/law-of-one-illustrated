# Law of One Illustrated 🌟

Educational illustrated storybooks explaining Law of One concepts. Transform complex spiritual teachings from the Ra Material into easy-to-understand visual guides.

## What It Does

- Converts Law of One concepts into illustrated educational storybooks
- Each category (Densities, Energy Centers, Archetypical Mind, etc.) becomes a multi-page guide
- Modern minimalist art style for clarity and spiritual aesthetic
- Available in Spanish for wider accessibility
- Generates PDF storybooks perfect for learning, practice, and teaching

## Core Features

- **38+ Categories**: All major Law of One topics organized and illustrated
- **Educational Focus**: Complex concepts broken down into digestible pages
- **Visual Learning**: Illustrations enhance understanding of abstract spiritual ideas
- **PDF Export**: Share and distribute educational materials
- **Web Gallery**: Browse and view all generated storybooks

## Quick Start

```bash
# Get uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/LuisReinoso/law-of-one-illustrated
cd law-of-one-illustrated
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Add your FAL key for image generation
cp .env.example .env
# Edit .env - add FAL_KEY from https://fal.ai

# Copy MCP config
cp .mcp.json.template .mcp.json

# Generate your first Law of One storybook
python create_story.py "Las Siete Densidades de Consciencia"
```

## Example Categories to Generate

**Foundational Concepts:**
```bash
python create_story.py "Las Densidades - Niveles de Consciencia"
python create_story.py "Los Centros Energéticos - Chakras"
python create_story.py "La Ley del Uno - Principio Fundamental"
```

**Advanced Topics:**
```bash
python create_story.py "La Mente Arquetípica - Los Arquetipos"
python create_story.py "El Tarot y los 22 Arquetipos"
python create_story.py "Transferencia de Energía Sexual"
```

**Practical Teachings:**
```bash
python create_story.py "Balanceo y Sanación"
python create_story.py "Meditación según Ra"
python create_story.py "Servicio a Otros vs Servicio a Sí Mismo"
```

## Web Interface

```bash
# Start the beautiful web interface
cd frontend
python app_simple.py
# Opens browser at http://localhost:8080

# Create Law of One storybooks visually
# Browse generated content in the gallery
# View with page-flip animation
```

## Output Structure

```
stories/las-densidades/
├── story_data.json       # Complete storybook data
├── storybook.pdf         # Ready to share/print
└── images/               # All illustrations
    ├── style_reference.jpeg
    ├── page_01.jpeg
    ├── page_02.jpeg
    └── ...
```

## Law of One Categories

The system supports all major Ra Material categories:

- **Densities** (7 levels of consciousness)
- **Energy Centers** (Chakras and energy work)
- **Archetypical Mind** (22 Archetypes)
- **Tarot** (Archetypal correspondences)
- **Harvest** (Graduation to 4th density)
- **Balancing & Healing**
- **Meditation**
- **Service to Others**
- **The Two Paths** (STO vs STS)
- **Cosmology** (Creation and intelligent infinity)
- **Earth History** (Wanderers, Ra contact, pyramids)
- And 25+ more categories

## Requirements

- Python 3.11+
- FAL API key from https://fal.ai
- Basic understanding of Law of One material (recommended but not required)

## Purpose

This tool helps:
- **Learn**: Visual aids make complex concepts easier to grasp
- **Practice**: Review and internalize Law of One teachings
- **Teach**: Create educational materials to share with others
- **Explore**: Discover connections between different concepts

## Technical Foundation

Built on the Claude Code SDK storybook framework with:
- Autonomous AI agent for content structuring
- Nano-Banana image generation for consistency
- MCP tools for image generation and PDF creation
- FastAPI web interface for easy access

## Security

This repository includes security hardening:
- Input validation to prevent command injection
- Path traversal protection for file serving
- Safe subprocess handling
- Sanitized user inputs

---

**Note**: This is an educational tool for exploring Law of One concepts. For original source material, visit [lawofone.info](https://www.lawofone.info/)

Based on the story generation framework with adaptations for spiritual/educational content.
