#!/usr/bin/env python3
"""
Law of One Categories Browser

Browse all 38+ Law of One topics and generate educational storybooks
for any concept from the Ra Material.
"""

import json
import sys
import os
import asyncio
from pathlib import Path
from typing import Dict, List, Any

def load_categories() -> Dict[str, Any]:
    """Load the categories database"""
    categories_file = Path("law_of_one_categories.json")
    if not categories_file.exists():
        print("❌ Categories database not found")
        sys.exit(1)

    with open(categories_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def print_header():
    """Print header"""
    print("=" * 70)
    print("📚 NAVEGADOR DE CATEGORÍAS DE LA LEY DEL UNO / RA MATERIAL")
    print("=" * 70)
    print()

def list_all_categories(categories_data: Dict[str, Any]):
    """List all main categories"""
    print("TODAS LAS CATEGORÍAS PRINCIPALES:\n")

    categories = categories_data["categories"]

    # Group by difficulty
    beginner = [c for c in categories if c.get("difficulty") == "beginner"]
    foundational = [c for c in categories if c.get("difficulty") == "foundational"]
    intermediate = [c for c in categories if c.get("difficulty") == "intermediate"]
    advanced = [c for c in categories if c.get("difficulty") == "advanced"]

    if foundational:
        print("🌱 CONCEPTOS FUNDAMENTALES:")
        for i, cat in enumerate(foundational, 1):
            subcats = f" ({len(cat.get('subcategories', []))} subcategorías)" if cat.get('subcategories') else ""
            print(f"  {i}. {cat['name_es']}{subcats}")
        print()

    if beginner:
        print("🔰 PRINCIPIANTES:")
        for i, cat in enumerate(beginner, 1):
            print(f"  {i}. {cat['name_es']}")
        print()

    if intermediate:
        print("📖 NIVEL INTERMEDIO:")
        for i, cat in enumerate(intermediate, 1):
            subcats = f" ({len(cat.get('subcategories', []))} subcategorías)" if cat.get('subcategories') else ""
            print(f"  {i}. {cat['name_es']}{subcats}")
        print()

    if advanced:
        print("🔬 NIVEL AVANZADO:")
        for i, cat in enumerate(advanced, 1):
            subcats = f" ({len(cat.get('subcategories', []))} subcategorías)" if cat.get('subcategories') else ""
            print(f"  {i}. {cat['name_es']}{subcats}")
        print()

def show_category_detail(category: Dict[str, Any]):
    """Show detailed information about a category"""
    print("\n" + "=" * 70)
    print(f"📖 {category['name_es']}")
    print("=" * 70)
    print(f"\nNombre en inglés: {category['name_en']}")
    print(f"Nivel: {category.get('difficulty', 'N/A').title()}")
    print(f"Páginas recomendadas: {category.get('recommended_pages', 8)}")

    if category.get('description_es'):
        print(f"\nDescripción:")
        print(f"  {category['description_es']}")

    if category.get('key_concepts'):
        print(f"\nConceptos clave:")
        for concept in category['key_concepts']:
            print(f"  • {concept}")

    if category.get('subcategories'):
        print(f"\nSubcategorías ({len(category['subcategories'])}):")
        for subcat in category['subcategories']:
            if isinstance(subcat, dict):
                print(f"  • {subcat.get('name_es', subcat.get('id', 'Unknown'))}")
            else:
                print(f"  • {subcat}")

    print("\nPara generar este contenido educativo, usa:")
    print(f"  python create_law_of_one.py \"{category['name_es']}\"")
    print()

def show_learning_paths(categories_data: Dict[str, Any]):
    """Show recommended learning paths"""
    print("\n" + "=" * 70)
    print("🎓 CAMINOS DE APRENDIZAJE RECOMENDADOS")
    print("=" * 70)

    paths = categories_data.get("learning_paths", {})
    categories = {c['id']: c for c in categories_data['categories']}

    for level, path_data in paths.items():
        print(f"\n{path_data['name_es'].upper()}:")
        for i, cat_id in enumerate(path_data['recommended_order'], 1):
            cat = categories.get(cat_id)
            if cat:
                print(f"  {i}. {cat['name_es']}")
    print()

def search_categories(query: str, categories_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Search categories by keyword"""
    query_lower = query.lower()
    results = []

    for cat in categories_data['categories']:
        # Search in name, description, and key concepts
        if (query_lower in cat['name_es'].lower() or
            query_lower in cat['name_en'].lower() or
            query_lower in cat.get('description_es', '').lower() or
            any(query_lower in concept.lower() for concept in cat.get('key_concepts', []))):
            results.append(cat)

    return results

def interactive_mode(categories_data: Dict[str, Any]):
    """Interactive category browser"""
    while True:
        print("\n" + "=" * 70)
        print("OPCIONES:")
        print("  1. Ver todas las categorías")
        print("  2. Ver caminos de aprendizaje")
        print("  3. Buscar por palabra clave")
        print("  4. Ver detalles de una categoría")
        print("  5. Generar contenido educativo")
        print("  0. Salir")
        print("=" * 70)

        choice = input("\nElige una opción (0-5): ").strip()

        if choice == "0":
            print("\n¡Hasta pronto! 🌟")
            break

        elif choice == "1":
            list_all_categories(categories_data)

        elif choice == "2":
            show_learning_paths(categories_data)

        elif choice == "3":
            query = input("\nPalabra clave a buscar: ").strip()
            results = search_categories(query, categories_data)
            if results:
                print(f"\n📚 Encontradas {len(results)} categorías:")
                for i, cat in enumerate(results, 1):
                    print(f"  {i}. {cat['name_es']}")

                detail = input("\n¿Ver detalles de alguna? (número o Enter para continuar): ").strip()
                if detail.isdigit() and 1 <= int(detail) <= len(results):
                    show_category_detail(results[int(detail) - 1])
            else:
                print(f"\n❌ No se encontraron categorías con '{query}'")

        elif choice == "4":
            list_all_categories(categories_data)
            cat_name = input("\nNombre de la categoría (español): ").strip()

            # Find category
            found = None
            for cat in categories_data['categories']:
                if cat['name_es'].lower() == cat_name.lower():
                    found = cat
                    break

            if found:
                show_category_detail(found)
            else:
                print(f"\n❌ Categoría '{cat_name}' no encontrada")

        elif choice == "5":
            list_all_categories(categories_data)
            cat_name = input("\nNombre de la categoría a generar: ").strip()

            # Find category
            found = None
            for cat in categories_data['categories']:
                if cat['name_es'].lower() == cat_name.lower():
                    found = cat
                    break

            if found:
                print(f"\n🎨 Generando: {found['name_es']}...")
                print(f"   Ejecutando: python create_law_of_one.py \"{found['name_es']}\"\n")

                # Import and run
                from sdk_launcher import AutonomousStoryCreator

                class LawOfOneEducator(AutonomousStoryCreator):
                    def _load_system_prompt(self) -> str:
                        prompt_path = Path("law_of_one_system_prompt.txt")
                        return prompt_path.read_text(encoding="utf-8")

                async def generate():
                    educator = LawOfOneEducator()
                    result = await educator.create_story(found['name_es'])
                    if result["success"]:
                        print("\n✅ ¡Contenido educativo generado exitosamente!")
                    else:
                        print(f"\n❌ Error: {result.get('error', 'Unknown')}")

                asyncio.run(generate())
            else:
                print(f"\n❌ Categoría '{cat_name}' no encontrada")

def main():
    """Main entry point"""
    categories_data = load_categories()

    print_header()
    print(f"Total de categorías: {categories_data['metadata']['total_categories']}")
    print(f"Fuente: {categories_data['metadata']['source']}")
    print(f"Última actualización: {categories_data['metadata']['last_updated']}\n")

    if len(sys.argv) > 1:
        # Command line mode
        command = sys.argv[1].lower()

        if command in ["list", "listar", "l"]:
            list_all_categories(categories_data)

        elif command in ["paths", "caminos", "p"]:
            show_learning_paths(categories_data)

        elif command in ["search", "buscar", "s"]:
            if len(sys.argv) > 2:
                query = " ".join(sys.argv[2:])
                results = search_categories(query, categories_data)
                if results:
                    print(f"📚 Encontradas {len(results)} categorías:\n")
                    for cat in results:
                        print(f"  • {cat['name_es']}")
                        print(f"    {cat.get('description_es', '')}\n")
                else:
                    print(f"❌ No se encontraron categorías con '{query}'")
            else:
                print("❌ Uso: python browse_categories.py search <palabra>")

        elif command in ["detail", "detalle", "d"]:
            if len(sys.argv) > 2:
                cat_name = " ".join(sys.argv[2:])
                found = None
                for cat in categories_data['categories']:
                    if cat['name_es'].lower() == cat_name.lower():
                        found = cat
                        break

                if found:
                    show_category_detail(found)
                else:
                    print(f"❌ Categoría '{cat_name}' no encontrada")
            else:
                print("❌ Uso: python browse_categories.py detail <nombre>")

        else:
            print(f"❌ Comando desconocido: {command}")
            print("\nComandos disponibles:")
            print("  list     - Listar todas las categorías")
            print("  paths    - Ver caminos de aprendizaje")
            print("  search   - Buscar por palabra clave")
            print("  detail   - Ver detalles de una categoría")

    else:
        # Interactive mode
        interactive_mode(categories_data)

if __name__ == "__main__":
    main()
