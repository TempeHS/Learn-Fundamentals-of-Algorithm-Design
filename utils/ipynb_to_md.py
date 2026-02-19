#!/usr/bin/env python3
"""Convert Jupyter notebooks to Markdown files."""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Iterable, List

try:
    import nbformat
    from nbconvert import MarkdownExporter
    from nbformat import ValidationError
except ImportError:
    print(
        "❌ nbconvert not available. Install dependencies with: bash utils/install_dependencies.sh"
    )
    sys.exit(1)

# Playwright-based PNG renderer for draw.io diagrams
try:
    from drawio_to_png import render_iframe_url_to_png

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def log(message: str, verbose: bool) -> None:
    if verbose:
        print(message)


def find_notebooks(input_dir: Path, pattern: str) -> List[Path]:
    return sorted(input_dir.glob(pattern))


def replace_iframes_with_png(content: str, output_dir: Path, verbose: bool) -> str:
    """Replace draw.io iframes with PNG image references."""
    if not PLAYWRIGHT_AVAILABLE:
        log("⚠️  Playwright not available - iframes will remain as-is", verbose)
        return content

    assets_dir = output_dir / "drawio_assets"

    def repl(match):
        src = match.group(1)
        try:
            digest = hashlib.sha1(src.encode("utf-8")).hexdigest()[:16]
            log(f"  🎨 Rendering diagram [{digest[:8]}]", verbose)

            _, png_path = render_iframe_url_to_png(src, cache_dir=assets_dir)
            # Use relative path for markdown
            rel_path = png_path.relative_to(output_dir)

            return f"![Flowchart diagram]({rel_path})"

        except Exception as e:
            log(f"  ⚠️  Failed to render diagram: {e}", verbose)
            return match.group(0)  # Keep original iframe

    iframe_pattern = (
        r'<iframe[^>]+src="([^" ]*viewer\.diagrams\.net[^"]+)"[^>]*></iframe>'
    )
    return re.sub(iframe_pattern, repl, content, flags=re.IGNORECASE)


def convert_notebook(
    notebook_path: Path, output_dir: Path, exporter: MarkdownExporter, verbose: bool
) -> Path:
    log(f"Converting {notebook_path} -> Markdown", verbose)
    nb_node = load_notebook(notebook_path, verbose)

    resources = {"output_files_dir": f"{notebook_path.stem}_files"}
    body, resources = exporter.from_notebook_node(nb_node, resources=resources)

    # Replace draw.io iframes with PNG images
    body = replace_iframes_with_png(body, output_dir, verbose)

    # Remove "_Click the diagram to open in full editor_" lines
    body = re.sub(r"_Click the diagram to open in full editor_\n?", "", body)

    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / f"{notebook_path.stem}.md"
    md_path.write_text(body, encoding="utf-8")

    outputs = resources.get("outputs", {})
    for name, data in outputs.items():
        asset_path = output_dir / name
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        with open(asset_path, "wb") as asset_file:
            asset_file.write(data)
        log(f"  wrote asset {asset_path}", verbose)

    return md_path


def convert_all(notebooks: Iterable[Path], output_dir: Path, verbose: bool) -> int:
    exporter = MarkdownExporter()
    count = 0

    for notebook_path in notebooks:
        convert_notebook(notebook_path, output_dir, exporter, verbose)
        count += 1

    return count


def load_notebook(notebook_path: Path, verbose: bool):
    """Load a notebook, repairing minimal JSON-only files if needed."""

    def _repair_minimal(payload) -> dict:
        """Best-effort repair for minimally structured JSON files."""

        # If the payload is not a dict (e.g., a raw list of cells), wrap it.
        if not isinstance(payload, dict):
            payload = {"cells": payload if isinstance(payload, list) else []}

        # Ensure required top-level keys exist
        payload.setdefault("cells", [])
        payload.setdefault("metadata", {})
        payload.setdefault("nbformat", 4)
        payload.setdefault("nbformat_minor", 5)

        repaired_cells = []
        for cell in payload.get("cells", []):
            # Flatten common list-wrapped cell shapes
            if isinstance(cell, list):
                cell = next((c for c in cell if isinstance(c, dict)), None)
            # Promote plain strings to markdown cells so nbconvert can proceed
            if isinstance(cell, str):
                cell = {"cell_type": "markdown", "metadata": {}, "source": cell}
            if not isinstance(cell, dict):
                continue

            # Normalize metadata and source fields
            metadata = cell.get("metadata")
            cell["metadata"] = metadata if isinstance(metadata, dict) else {}

            source = cell.get("source", "")
            if isinstance(source, list):
                source = "".join(source)
            elif source is None:
                source = ""
            cell["source"] = source

            # Ensure minimal required fields exist for nbconvert
            cell.setdefault("cell_type", "markdown")
            cell.setdefault("outputs", [])
            cell.setdefault("execution_count", None)

            repaired_cells.append(cell)

        payload["cells"] = repaired_cells
        return payload

    try:
        return nbformat.read(notebook_path, as_version=4)
    except (ValidationError, AttributeError, json.JSONDecodeError) as err:
        log(
            f"⚠️  Notebook {notebook_path} is missing nbformat fields; attempting repair ({err})",
            verbose,
        )
        with open(notebook_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        repaired = _repair_minimal(data)
        return nbformat.from_dict(repaired)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert .ipynb notebooks to Markdown."
    )
    parser.add_argument(
        "--input-dir",
        default="lessons",
        type=Path,
        help="Directory containing .ipynb files",
    )
    parser.add_argument(
        "--output-dir",
        default="other_formats/markdown_lessons",
        type=Path,
        help="Directory to write .md files",
    )
    parser.add_argument(
        "--pattern",
        default="*.ipynb",
        help="Glob pattern for notebooks inside input-dir",
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Convert a single notebook instead of scanning input-dir",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.file:
        notebooks = [args.file]
    else:
        notebooks = find_notebooks(args.input_dir, args.pattern)

    if not notebooks:
        print("No notebooks found to convert.")
        return

    converted = convert_all(notebooks, args.output_dir, args.verbose)
    print(f"Converted {converted} notebook(s) to Markdown in {args.output_dir}")


if __name__ == "__main__":
    main()
