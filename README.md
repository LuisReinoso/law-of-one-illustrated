# Law of One Illustrated 🌟

Educational illustrated storybooks explaining Law of One concepts. Transform complex spiritual teachings from the Ra Material into easy-to-understand visual guides in Spanish.

## What It Does

- Converts authentic Ra Material concepts into illustrated educational storybooks
- **39 categories** covering all major Law of One topics from lawofone.info
- All content in **Spanish** (castellano) for accessibility
- Educational diagram style focused on clarity and understanding
- Generates PDF storybooks perfect for learning, practice, and teaching
- Based on authentic Ra channeling (1981-1984) by L/L Research

## Core Features

- **Category Database**: 39 organized Law of One topics with learning paths
- **Accurate Ra Material**: Proper terminology (complejos de memoria social, cosecha, etc.)
- **Interactive Browser**: Search and explore all categories
- **Educational Focus**: Complex concepts broken down into digestible pages
- **Visual Learning**: Minimalist diagrams enhance understanding
- **PDF Export**: Share and distribute educational materials

## Quick Start

```bash
# Clone and setup
git clone https://github.com/LuisReinoso/law-of-one-illustrated
cd law-of-one-illustrated
pip install -r requirements.txt

# Add your FAL key for image generation
cp .env.example .env
# Edit .env - add FAL_KEY from https://fal.ai

# Copy MCP config
cp .mcp.json.template .mcp.json

# Browse all available categories
python browse_categories.py

# Generate your first Law of One educational storybook
python create_law_of_one.py "Las Siete Densidades según Ra"
```

## Browse Categories

```bash
# Interactive browser - explore all 39 categories
python browse_categories.py

# List all categories organized by difficulty
python browse_categories.py list

# Search for specific topics
python browse_categories.py search "servicio"
python browse_categories.py search "densidades"

# View category details
python browse_categories.py detail "Los Dos Caminos"

# See recommended learning paths
python browse_categories.py paths
```

## Example Categories to Generate

**Foundational Concepts (8 categories):**
```bash
python create_law_of_one.py "Las Densidades"
python create_law_of_one.py "La Ley del Uno"
python create_law_of_one.py "Los Dos Caminos"
python create_law_of_one.py "La Cosecha"
python create_law_of_one.py "Ra"
python create_law_of_one.py "El Contacto con Ra"
```

**Intermediate Topics (16 categories):**
```bash
python create_law_of_one.py "Centros de Energía"
python create_law_of_one.py "Balanceo"
python create_law_of_one.py "Los Errantes"
python create_law_of_one.py "El Velo del Olvido"
python create_law_of_one.py "La Confederación de Planetas"
```

**Advanced Topics (8 categories):**
```bash
python create_law_of_one.py "La Mente Arquetípica"
python create_law_of_one.py "El Tarot"
python create_law_of_one.py "Cosmología"
python create_law_of_one.py "Tiempo/Espacio"
python create_law_of_one.py "Transferencia de Energía Sexual"
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
