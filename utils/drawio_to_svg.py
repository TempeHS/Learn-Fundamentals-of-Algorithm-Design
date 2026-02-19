#!/usr/bin/env python3
"""
Pure-Python draw.io (mxGraph) XML → SVG converter.

Converts the subset of mxGraphModel XML used in the lesson flowcharts
to standalone SVG images.  Zero external dependencies – stdlib only.

Supported shapes: terminal (rounded rect), rectangle, diamond (rhombus),
parallelogram, ellipse, rounded_rect, and text labels.
Supported edges: straight polylines with arrowheads, waypoints, and labels.

Usage
-----
    from drawio_to_svg import mxgraph_xml_to_svg

    svg_string = mxgraph_xml_to_svg(xml_string)
"""

from __future__ import annotations

import html
import math
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Style parser
# ---------------------------------------------------------------------------


def _parse_style(style_str: str) -> Dict[str, str]:
    """Parse an mxGraph style string like 'rounded=1;fillColor=#fff;shape=rhombus'."""
    result: Dict[str, str] = {}
    if not style_str:
        return result
    for part in style_str.split(";"):
        part = part.strip()
        if "=" in part:
            key, val = part.split("=", 1)
            result[key.strip()] = val.strip()
        elif part:
            # Bare token like "rhombus" → treat as shape
            result[part] = "1"
    return result


# ---------------------------------------------------------------------------
# Shape classification
# ---------------------------------------------------------------------------


def _classify_shape(style: Dict[str, str]) -> str:
    """Return a canonical shape name from the mxGraph style dict."""
    shape = style.get("shape", "")
    if shape == "parallelogram" or "parallelogramPerimeter" in style.get(
        "perimeter", ""
    ):
        return "parallelogram"
    if "rhombus" in style or shape == "rhombus":
        return "diamond"
    if "ellipse" in style or shape == "ellipse":
        return "ellipse"
    rounded = style.get("rounded", "0")
    arc = int(style.get("arcSize", "0") or "0")
    if rounded == "1" and arc >= 40:
        return "terminal"  # Start/End pill shape
    if rounded == "1":
        return "rounded_rect"
    return "rectangle"


# ---------------------------------------------------------------------------
# SVG primitives
# ---------------------------------------------------------------------------

_SVG_NS = 'xmlns="http://www.w3.org/2000/svg"'
_ARROW_MARKER = (
    '<marker id="arrowhead" markerWidth="10" markerHeight="7" '
    'refX="10" refY="3.5" orient="auto" markerUnits="strokeWidth">'
    '<polygon points="0 0, 10 3.5, 0 7" fill="#000"/>'
    "</marker>"
)


def _rect_svg(
    x: float,
    y: float,
    w: float,
    h: float,
    rx: float = 0,
    ry: float = 0,
    fill: str = "#ffffff",
    stroke: str = "#000000",
    stroke_width: float = 2,
) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
        f'rx="{rx}" ry="{ry}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
    )


def _diamond_svg(
    cx: float,
    cy: float,
    w: float,
    h: float,
    fill: str = "#ffffff",
    stroke: str = "#000000",
    stroke_width: float = 2,
) -> str:
    """Render a diamond (rhombus) centred at (cx, cy)."""
    hw, hh = w / 2, h / 2
    pts = f"{cx},{cy - hh} {cx + hw},{cy} {cx},{cy + hh} {cx - hw},{cy}"
    return (
        f'<polygon points="{pts}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
    )


def _parallelogram_svg(
    x: float,
    y: float,
    w: float,
    h: float,
    fill: str = "#ffffff",
    stroke: str = "#000000",
    stroke_width: float = 2,
) -> str:
    """Render a parallelogram with a fixed skew offset."""
    skew = min(h * 0.4, w * 0.15)
    pts = f"{x + skew},{y} {x + w},{y} " f"{x + w - skew},{y + h} {x},{y + h}"
    return (
        f'<polygon points="{pts}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
    )


def _ellipse_svg(
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    fill: str = "#ffffff",
    stroke: str = "#000000",
    stroke_width: float = 2,
) -> str:
    return (
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
    )


def _text_svg(
    x: float,
    y: float,
    text: str,
    font_size: float = 12,
    anchor: str = "middle",
    dominant_baseline: str = "central",
    font_weight: str = "normal",
) -> str:
    """Render one or more lines of text centred at (x, y)."""
    # Strip HTML tags that draw.io sometimes includes
    clean = re.sub(r"<[^>]+>", "", text)
    clean = html.unescape(clean).strip()
    if not clean:
        return ""

    lines = clean.split("\n")
    if len(lines) == 1:
        escaped = _escape_xml(lines[0])
        return (
            f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
            f'dominant-baseline="{dominant_baseline}" '
            f'font-family="Arial, Helvetica, sans-serif" font-size="{font_size}" '
            f'font-weight="{font_weight}" fill="#000">{escaped}</text>'
        )

    # Multi-line: use tspans
    parts = [
        f'<text x="{x}" text-anchor="{anchor}" '
        f'font-family="Arial, Helvetica, sans-serif" font-size="{font_size}" '
        f'font-weight="{font_weight}" fill="#000">'
    ]
    start_y = y - (len(lines) - 1) * font_size * 0.6
    for i, line in enumerate(lines):
        ly = start_y + i * font_size * 1.2
        escaped = _escape_xml(line)
        parts.append(
            f'<tspan x="{x}" y="{ly}" dominant-baseline="{dominant_baseline}">'
            f"{escaped}</tspan>"
        )
    parts.append("</text>")
    return "\n".join(parts)


def _escape_xml(s: str) -> str:
    """Escape text for safe embedding in XML/SVG."""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# ---------------------------------------------------------------------------
# Node rendering
# ---------------------------------------------------------------------------


def _render_node(
    shape: str,
    x: float,
    y: float,
    w: float,
    h: float,
    label: str,
    style: Dict[str, str],
) -> str:
    """Return SVG elements for a single flowchart node."""
    fill = style.get("fillColor", "#ffffff")
    stroke = style.get("strokeColor", "#000000")
    sw = float(style.get("strokeWidth", "2"))

    parts: List[str] = []

    if shape == "terminal":
        # Pill-shaped rounded rect
        rx = h / 2
        parts.append(
            _rect_svg(
                x, y, w, h, rx=rx, ry=rx, fill=fill, stroke=stroke, stroke_width=sw
            )
        )
    elif shape == "diamond":
        parts.append(
            _diamond_svg(
                x + w / 2, y + h / 2, w, h, fill=fill, stroke=stroke, stroke_width=sw
            )
        )
    elif shape == "parallelogram":
        parts.append(
            _parallelogram_svg(x, y, w, h, fill=fill, stroke=stroke, stroke_width=sw)
        )
    elif shape == "ellipse":
        parts.append(
            _ellipse_svg(
                x + w / 2,
                y + h / 2,
                w / 2,
                h / 2,
                fill=fill,
                stroke=stroke,
                stroke_width=sw,
            )
        )
    elif shape == "rounded_rect":
        parts.append(
            _rect_svg(x, y, w, h, rx=6, ry=6, fill=fill, stroke=stroke, stroke_width=sw)
        )
    else:  # rectangle / default
        parts.append(_rect_svg(x, y, w, h, fill=fill, stroke=stroke, stroke_width=sw))

    # Label inside the shape
    if label:
        font_size = min(12, h * 0.35, w * 0.12)
        font_size = max(9, font_size)
        parts.append(_text_svg(x + w / 2, y + h / 2, label, font_size=font_size))

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Edge rendering
# ---------------------------------------------------------------------------


def _connection_point(node: dict, px: float, py: float) -> Tuple[float, float]:
    """Compute the absolute connection point on a node's bounding box.

    px, py are fractions (0–1) of the node's width/height.
    """
    x = node["x"] + node["w"] * px
    y = node["y"] + node["h"] * py
    return x, y


def _render_edge(edge: dict, nodes: Dict[str, dict]) -> str:
    """Return SVG elements for an edge (polyline + optional label)."""
    style = edge["style"]
    source_id = edge.get("source")
    target_id = edge.get("target")

    # Connection point fractions
    ex_x = float(style.get("exitX", "0.5"))
    ex_y = float(style.get("exitY", "1"))
    en_x = float(style.get("entryX", "0.5"))
    en_y = float(style.get("entryY", "0"))

    points: List[Tuple[float, float]] = []

    # Start point
    if source_id and source_id in nodes:
        points.append(_connection_point(nodes[source_id], ex_x, ex_y))
    elif edge.get("source_point"):
        points.append(edge["source_point"])

    # Waypoints
    for wp in edge.get("waypoints", []):
        points.append(wp)

    # End point
    if target_id and target_id in nodes:
        points.append(_connection_point(nodes[target_id], en_x, en_y))
    elif edge.get("target_point"):
        points.append(edge["target_point"])

    if len(points) < 2:
        return ""

    # Build polyline
    pts_str = " ".join(f"{p[0]},{p[1]}" for p in points)
    stroke = style.get("strokeColor", "#000000")
    sw = float(style.get("strokeWidth", "2"))

    parts: List[str] = [
        f'<polyline points="{pts_str}" fill="none" '
        f'stroke="{stroke}" stroke-width="{sw}" '
        f'marker-end="url(#arrowhead)"/>'
    ]

    # Edge label (e.g. "True" / "False")
    label = edge.get("label", "")
    if label:
        # Place label at the midpoint of the first segment
        mid_idx = len(points) // 2
        mx = (points[mid_idx - 1][0] + points[mid_idx][0]) / 2
        my = (points[mid_idx - 1][1] + points[mid_idx][1]) / 2

        # Offset the label slightly away from the line
        dx = points[mid_idx][0] - points[mid_idx - 1][0]
        dy = points[mid_idx][1] - points[mid_idx - 1][1]
        length = math.hypot(dx, dy) or 1
        # Perpendicular offset (to the right of travel direction)
        offset = 10
        ox = -dy / length * offset
        oy = dx / length * offset

        # Background for readability
        tw = len(label) * 7 + 6
        parts.append(
            f'<rect x="{mx + ox - tw / 2}" y="{my + oy - 8}" '
            f'width="{tw}" height="16" fill="#ffffff" rx="2" ry="2" '
            f'stroke="none"/>'
        )
        parts.append(
            _text_svg(mx + ox, my + oy, label, font_size=11, font_weight="bold")
        )

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main converter
# ---------------------------------------------------------------------------


def mxgraph_xml_to_svg(xml_str: str, padding: int = 20) -> str:
    """Convert an mxGraphModel XML string to a standalone SVG string.

    Parameters
    ----------
    xml_str : str
        Raw mxGraphModel XML.
    padding : int
        Padding around the diagram in the SVG viewBox.

    Returns
    -------
    str
        Complete SVG document as a string.
    """
    root = ET.fromstring(xml_str.strip())

    # Collect all mxCell elements
    cells = root.findall(".//mxCell")

    nodes: Dict[str, dict] = {}
    edges: List[dict] = []

    for cell in cells:
        cell_id = cell.get("id", "")
        style_str = cell.get("style", "")
        style = _parse_style(style_str)
        value = cell.get("value", "")
        is_edge = cell.get("edge") == "1"
        is_vertex = cell.get("vertex") == "1"

        geom = cell.find("mxGeometry")

        if is_vertex and geom is not None:
            x = float(geom.get("x", "0"))
            y = float(geom.get("y", "0"))
            w = float(geom.get("width", "0"))
            h = float(geom.get("height", "0"))
            shape = _classify_shape(style)
            nodes[cell_id] = {
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "label": value,
                "shape": shape,
                "style": style,
            }
        elif is_edge:
            waypoints: List[Tuple[float, float]] = []
            source_point: Optional[Tuple[float, float]] = None
            target_point: Optional[Tuple[float, float]] = None

            if geom is not None:
                # Waypoints
                arr = geom.find("Array")
                if arr is not None:
                    for pt in arr.findall("mxPoint"):
                        px = float(pt.get("x", "0"))
                        py = float(pt.get("y", "0"))
                        waypoints.append((px, py))

                # Explicit source/target points (when no connected node)
                for pt in geom.findall("mxPoint"):
                    as_attr = pt.get("as", "")
                    px = float(pt.get("x", "0"))
                    py = float(pt.get("y", "0"))
                    if as_attr == "sourcePoint":
                        source_point = (px, py)
                    elif as_attr == "targetPoint":
                        target_point = (px, py)

            edges.append(
                {
                    "source": cell.get("source"),
                    "target": cell.get("target"),
                    "label": value,
                    "style": style,
                    "waypoints": waypoints,
                    "source_point": source_point,
                    "target_point": target_point,
                }
            )

    # ---- Calculate bounding box ----
    all_x: List[float] = []
    all_y: List[float] = []
    for n in nodes.values():
        all_x.extend([n["x"], n["x"] + n["w"]])
        all_y.extend([n["y"], n["y"] + n["h"]])
    for e in edges:
        for wp in e.get("waypoints", []):
            all_x.append(wp[0])
            all_y.append(wp[1])
        if e.get("source_point"):
            all_x.append(e["source_point"][0])
            all_y.append(e["source_point"][1])
        if e.get("target_point"):
            all_x.append(e["target_point"][0])
            all_y.append(e["target_point"][1])

    if not all_x or not all_y:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"/>'

    min_x = min(all_x) - padding
    min_y = min(all_y) - padding
    max_x = max(all_x) + padding
    max_y = max(all_y) + padding
    vw = max_x - min_x
    vh = max_y - min_y

    # ---- Assemble SVG ----
    svg_parts: List[str] = [
        f'<svg {_SVG_NS} viewBox="{min_x} {min_y} {vw} {vh}" '
        f'width="{vw}" height="{vh}" '
        f'style="background:#ffffff">',
        "<defs>",
        _ARROW_MARKER,
        "</defs>",
    ]

    # Render edges first (behind nodes)
    for edge in edges:
        svg_parts.append(_render_edge(edge, nodes))

    # Render nodes
    for node in nodes.values():
        svg_parts.append(
            _render_node(
                node["shape"],
                node["x"],
                node["y"],
                node["w"],
                node["h"],
                node["label"],
                node["style"],
            )
        )

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


# ---------------------------------------------------------------------------
# CLI helper
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python drawio_to_svg.py <input.xml> [output.svg]")
        sys.exit(1)
    in_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else in_path.rsplit(".", 1)[0] + ".svg"
    with open(in_path, "r", encoding="utf-8") as f:
        xml_data = f.read()
    svg = mxgraph_xml_to_svg(xml_data)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {out_path}")
