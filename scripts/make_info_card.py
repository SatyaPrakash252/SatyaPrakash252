#!/usr/bin/env python3
"""
Builds info-card.svg: a neofetch-style panel (title bar + key/value rows)
that fades/slides in line by line, then freezes. Content is hand-edited
below — update it whenever your role, stack, or highlights change.

    python scripts/make_info_card.py
"""

import os
import html

OUT_PATH = os.environ.get("INFO_CARD_OUT", "assets/info-card.svg")

USERNAME = "SatyaPrakash252"
NAME = "Satyaprakash Rout"

ROWS = [
    ("Now", "B.Tech CSE student (2023-2027)"),
    ("Role", "Full Stack Developer / AI Builder"),
    ("Stack", "Java, Python, React, Next.js, FastAPI, Flask"),
    ("AI/ML", "TensorFlow, Scikit-learn, CNNs, Agentic AI"),
    ("Highlight", "Built Project CURA - an agentic clinical docs platform"),
    ("Highlight", "CNN-based plant disease detector (TensorFlow + OpenCV)"),
    ("Goal", "Landing a product-based SWE role"),
]

WIDTH = 490
PAD = 20
TITLE_H = 34
ROW_H = 26
KEY_COL_W = 92

STAGGER_S = 0.12
FADE_S = 0.4
START_DELAY_S = 0.15


def build_svg() -> str:
    height = TITLE_H + PAD + len(ROWS) * ROW_H + PAD

    rows_svg = []
    for i, (key, val) in enumerate(ROWS):
        y = TITLE_H + PAD + i * ROW_H + 14
        delay = round(START_DELAY_S + i * STAGGER_S, 3)
        safe_key = html.escape(key)
        safe_val = html.escape(val)
        rows_svg.append(f'''
    <g class="line" style="animation-delay:{delay}s">
      <text class="key" x="{PAD}" y="{y}">{safe_key}</text>
      <text class="val" x="{PAD + KEY_COL_W}" y="{y}">{safe_val}</text>
    </g>''')

    total_delay = START_DELAY_S + len(ROWS) * STAGGER_S

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}" role="img" aria-label="Profile summary card for {html.escape(NAME)}">
  <defs>
    <style>
      .card-bg {{ fill: #0d1117; }}
      .card-border {{ fill: none; stroke: #21262d; stroke-width: 1.5; }}
      .titlebar {{ fill: #161b22; }}
      .dot {{ opacity: 0.9; }}
      .title-text {{
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        font-size: 12.5px; fill: #58a6ff;
      }}
      .key {{
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        font-size: 12px; font-weight: bold; fill: #7ee787;
      }}
      .val {{
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        font-size: 12px; fill: #c9d1d9;
      }}
      .line {{
        opacity: 0;
        transform: translateX(-6px);
        animation: fadein {FADE_S}s ease-out forwards;
      }}
      @keyframes fadein {{
        to {{ opacity: 1; transform: translateX(0); }}
      }}
      .cursor {{
        fill: #7ee787;
        animation: blink 1s steps(1) infinite;
        animation-delay: {total_delay}s;
      }}
      @keyframes blink {{ 0%, 49% {{ opacity: 1; }} 50%, 100% {{ opacity: 0; }} }}
    </style>
  </defs>

  <rect class="card-bg" x="0" y="0" width="{WIDTH}" height="{height}" rx="10"/>
  <rect class="titlebar" x="0" y="0" width="{WIDTH}" height="{TITLE_H}" rx="10"/>
  <rect x="0" y="{TITLE_H - 10}" width="{WIDTH}" height="10" fill="#161b22"/>
  <rect class="card-border" x="1" y="1" width="{WIDTH - 2}" height="{height - 2}" rx="10"/>

  <circle class="dot" cx="18" cy="{TITLE_H/2}" r="4" fill="#ff5f56"/>
  <circle class="dot" cx="32" cy="{TITLE_H/2}" r="4" fill="#ffbd2e"/>
  <circle class="dot" cx="46" cy="{TITLE_H/2}" r="4" fill="#27c93f"/>
  <text class="title-text" x="{WIDTH - PAD}" y="{TITLE_H/2 + 4}" text-anchor="end">neofetch --user {html.escape(USERNAME)}</text>

  {''.join(rows_svg)}
  <rect class="cursor" x="{PAD}" y="{height - PAD - 2}" width="7" height="12"/>
</svg>
'''
    return svg


def main():
    svg = build_svg()
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
