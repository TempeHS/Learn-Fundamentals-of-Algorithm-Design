#!/usr/bin/env python3
"""
Render draw.io diagrams to PNG using Playwright (headless Chromium).

This module takes either:
1. A full viewer.diagrams.net URL with embedded XML
2. Raw mxGraphModel XML string

And renders it to a PNG image using a headless browser.

Usage:
    from drawio_to_png import render_drawio_to_png

    # From URL
    png_bytes = render_drawio_to_png(iframe_url)

    # From XML
    png_bytes = render_drawio_to_png(xml_string, is_xml=True)
"""

from __future__ import annotations

import hashlib
import urllib.parse
from pathlib import Path
from typing import Optional

# Lazy import Playwright to avoid startup cost if not needed
_playwright = None
_browser = None


def _get_browser():
    """Lazy-load and cache the Playwright browser instance."""
    global _playwright, _browser
    if _browser is None:
        from playwright.sync_api import sync_playwright

        _playwright = sync_playwright().start()
        _browser = _playwright.chromium.launch()
    return _browser


def _close_browser():
    """Clean up browser resources."""
    global _playwright, _browser
    if _browser:
        _browser.close()
        _browser = None
    if _playwright:
        _playwright.stop()
        _playwright = None


def xml_to_viewer_url(xml: str) -> str:
    """Convert mxGraphModel XML to a viewer.diagrams.net URL."""
    encoded = urllib.parse.quote(xml)
    return f"https://viewer.diagrams.net/?nav=1#R{encoded}"


def render_drawio_to_png(
    source: str,
    is_xml: bool = False,
    width: int = 800,
    height: int = 600,
    wait_ms: int = 2000,
    output_path: Optional[Path] = None,
) -> bytes:
    """Render a draw.io diagram to PNG.

    Args:
        source: Either a viewer.diagrams.net URL or raw mxGraphModel XML
        is_xml: If True, treat source as XML; if False, as URL
        width: Viewport width in pixels
        height: Viewport height in pixels
        wait_ms: Time to wait for diagram to render (ms)
        output_path: Optional path to save the PNG file

    Returns:
        PNG image data as bytes
    """
    if is_xml:
        url = xml_to_viewer_url(source)
    else:
        url = source

    browser = _get_browser()
    page = browser.new_page(viewport={"width": width, "height": height})

    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(wait_ms)

        png_data = page.screenshot()

        if output_path:
            output_path.write_bytes(png_data)

        return png_data
    finally:
        page.close()


def render_iframe_url_to_png(
    iframe_url: str,
    cache_dir: Optional[Path] = None,
) -> tuple[bytes, Path]:
    """Render a draw.io iframe URL to PNG with caching.

    Args:
        iframe_url: Full viewer.diagrams.net URL from an iframe src
        cache_dir: Directory to cache rendered PNGs

    Returns:
        Tuple of (png_bytes, cache_file_path)
    """
    # Create hash for caching
    digest = hashlib.sha1(iframe_url.encode("utf-8")).hexdigest()[:16]

    if cache_dir:
        cache_dir.mkdir(exist_ok=True)
        cache_file = cache_dir / f"diagram_{digest}.png"

        if cache_file.exists():
            return cache_file.read_bytes(), cache_file
    else:
        cache_file = Path(f"/tmp/diagram_{digest}.png")

    png_data = render_drawio_to_png(iframe_url, is_xml=False)
    cache_file.write_bytes(png_data)

    return png_data, cache_file


# Cleanup on module unload
import atexit

atexit.register(_close_browser)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python drawio_to_png.py <url_or_xml_file> [output.png]")
        sys.exit(1)

    source = sys.argv[1]
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("output.png")

    # Check if it's a file
    if Path(source).exists():
        xml = Path(source).read_text()
        png = render_drawio_to_png(xml, is_xml=True, output_path=out_path)
    else:
        png = render_drawio_to_png(source, is_xml=False, output_path=out_path)

    print(f"Saved {len(png)} bytes to {out_path}")
