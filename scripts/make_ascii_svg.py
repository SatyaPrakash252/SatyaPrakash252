#!/usr/bin/env python3
"""
Converts source-prepped.png into avi-ascii.svg: a monochrome ASCII
portrait that types itself in row by row, then freezes (no looping).

Run locally after prep_photo.py, once per photo:

    python scripts/make_ascii_svg.py
"""

import os
import html
from PIL import Image

IN_PATH = os.environ.get("PREPPED_IMAGE", "source-prepped.png")
OUT_PATH = os.environ.get("ASCII_OUT", "assets/avi-ascii.svg")

# bright (sparse) -> dark (dense); leading space clears background to nothing
RAMP = " .`:-=+*cs#%@"

COLS = 100
ROWS = 53

CHAR_W = 5.6
CHAR_H = 10
PAD = 14
FILL_COLOR = "#c9d1d9"   # single light-gray fill — no per-char color, stays clean

ROW_WIPE_S = 0.6          # time for one row to wipe in
ROW_STAGGER_S = 0.045     # delay added per subsequent row


def to_ascii_lines(img: Image.Image, cols: int, rows: int):
    img = img.convert("L").resize((cols, rows))
    px = list(img.getdata())
    lines = []
    for y in range(rows):
        row = []
        for x in range(cols):
            lum = px[y * cols + x]
            idx = int((lum / 255) * (len(RAMP) - 1))
            row.append(RAMP[idx])
        lines.append("".join(row))
    return lines


def build_svg(lines) -> str:
    width = PAD * 2 + COLS * CHAR_W
    height = PAD * 2 + ROWS * CHAR_H

    rows_svg = []
    for i, line in enumerate(lines):
        y = PAD + (i + 1) * CHAR_H
        safe = html.escape(line).replace(" ", "&#160;")
        delay = round(i * ROW_STAGGER_S, 3)
        row_width = len(line) * CHAR_W
        rows_svg.append(f'''
    <g class="row" style="animation-delay:{delay}s">
      <clipPath id="rowclip{i}"><rect x="0" y="0" width="0" height="{CHAR_H + 2}"><animate attributeName="width" from="0" to="{row_width}" dur="{ROW_WIPE_S}s" begin="{delay}s" fill="freeze"/></rect></clipPath>
      <text class="ascii-row" x="{PAD}" y="{y}" clip-path="url(#rowclip{i})">{safe}</text>
      <rect class="cursor" x="{PAD}" y="{y - CHAR_H + 2}" width="2" height="{CHAR_H}">
        <animate attributeName="x" from="{PAD}" to="{PAD + row_width}" dur="{ROW_WIPE_S}s" begin="{delay}s" fill="freeze"/>
        <animate attributeName="opacity" from="1" to="0" dur="0.15s" begin="{delay + ROW_WIPE_S}s" fill="freeze"/>
      </rect>
    </g>''')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="ASCII portrait">
  <style>
    .ascii-row {{
      font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
      font-size: 9px;
      fill: {FILL_COLOR};
      white-space: pre;
    }}
    .cursor {{ fill: {FILL_COLOR}; }}
  </style>
  {''.join(rows_svg)}
</svg>
'''
    return svg


def main():
    if not os.path.exists(IN_PATH):
        raise SystemExit(
            f"{IN_PATH} not found. Run scripts/prep_photo.py your-photo.jpg first."
        )
    img = Image.open(IN_PATH)
    lines = to_ascii_lines(img, COLS, ROWS)
    svg = build_svg(lines)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
