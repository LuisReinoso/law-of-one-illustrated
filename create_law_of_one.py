#!/usr/bin/env python3
"""
Law of One Educational Storybook Creator

Creates accurate, illustrated educational materials about Ra Material/Law of One
concepts in Spanish, based on authentic teachings from lawofone.info
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the autonomous creator but with Law of One system prompt
from sdk_launcher import AutonomousStoryCreator

class LawOfOneEducator(AutonomousStoryCreator):
    """Educational storybook creator specialized for Law of One / Ra Material"""

    def _load_system_prompt(self) -> str:
        """Load the Law of One specialized system prompt"""
        prompt_path = Path("law_of_one_system_prompt.txt")
        if not prompt_path.exists():
            raise FileNotFoundError(f"Law of One system prompt not found: {prompt_path}")

        return prompt_path.read_text(encoding="utf-8")

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
                i += 1
            else:
                print("❌ --timeout requires a value in minutes")
                sys.exit(1)
        else:
            topic_parts.append(arg)
        i += 1

    if debug_mode:
        os.environ['VERBOSE'] = '1'

    return debug_mode, verbose_mode, timeout_minutes, " ".join(topic_parts)

async def main():
    debug_mode, verbose_mode, timeout_minutes, topic = parse_args()

    if not topic:
        print("Law of One Educational Storybook Creator")
        print("=" * 50)
        print("Creates illustrated educational content in SPANISH")
        print("based on authentic Ra Material teachings\n")
        print("Usage: python create_law_of_one.py \"concepto de la Ley del Uno\"\n")
        print("Examples:")
        print("  python create_law_of_one.py \"Las Siete Densidades según Ra\"")
        print("  python create_law_of_one.py \"Los Dos Caminos: Servicio a Otros vs Servicio a Sí Mismo\"")
        print("  python create_law_of_one.py \"Los Centros de Energía y el Balanceo\"")
        print("  python create_law_of_one.py \"La Mente Arquetípica y el Tarot\"")
        print("  python create_law_of_one.py \"Cosecha: Graduación entre Densidades\"")
        print("  python create_law_of_one.py \"Errantes: Voluntarios de Densidades Superiores\"")
        print("\nOptions: --debug --verbose --timeout 30")
        print("\nSource: lawofone.info (Ra Material channeled 1981-1984)")
        return

    print(f"Concepto de la Ley del Uno: {topic}")
    if debug_mode:
        print("Modo debug activado")
    if timeout_minutes:
        print(f"Tiempo límite: {timeout_minutes} minutos")

    # Verify environment setup
    if not os.getenv("FAL_KEY"):
        print("❌ FAL_KEY no encontrado en archivo .env")
        print("   Necesitas una API key de https://fal.ai")
        return

    if not Path(".mcp.json").exists():
        print("❌ .mcp.json no encontrado - copia desde .mcp.json.template")
        return

    # Ensure stories directory exists
    Path("stories").mkdir(parents=True, exist_ok=True)

    try:
        # Initialize Law of One educator
        educator = LawOfOneEducator()

        # Create educational storybook
        print("\nGenerando contenido educativo de la Ley del Uno...")
        result = await educator.create_story(topic)

        # Show results
        if result["success"]:
            stories_path = Path("stories")
            if stories_path.exists():
                story_dirs = list(stories_path.glob("*"))
                if story_dirs:
                    latest_dir = max(story_dirs, key=lambda p: p.stat().st_mtime)
                    print(f"\n✓ Contenido educativo guardado en: {latest_dir}/")
                    print(f"  - PDF: {latest_dir}/storybook.pdf")
                    print(f"  - JSON: {latest_dir}/story_data.json")
                    print(f"  - Imágenes: {latest_dir}/images/")
        else:
            if "error" in result:
                print(f"❌ {result['error']}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
