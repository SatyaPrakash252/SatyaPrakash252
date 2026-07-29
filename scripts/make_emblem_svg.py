#!/usr/bin/env python3
"""
Builds emblem.svg: a circular instrument-dial badge with YOUR OWN logo
image at the center — glowing rings, tick marks, and a slow rotating
sweep. This embeds your logo file directly (base64) so the badge is
one self-contained SVG.

Put your logo file here (any PNG/JPG/SVG works, ideally square,
transparent background looks best):

    D:\\GitProfile\\SatyaPrakash252\\IMAGES\\logo.png

...or pass a different path:

    python scripts/make_emblem_svg.py "D:\\path\\to\\your-logo.png"
"""

import os
import sys
import math
import base64
import mimetypes

OUT_PATH = os.environ.get("EMBLEM_OUT", "assets/emblem.svg")
DEFAULT_LOGO_PATH = r"D:\GitProfile\SatyaPrakash252\IMAGES\logo.png"

SIZE = 280
CX = SIZE / 2
CY = SIZE / 2

BG = "#050b14"
CYAN = "#7fd8ff"
CYAN_BRIGHT = "#eaf9ff"
CYAN_DIM = "#1c4a66"

LOGO_R = SIZE * 0.24  # radius of the logo image area at the center


def ticks(radius, count, length=8, opacity=0.55):
    parts = []
    for i in range(count):
        angle = (2 * math.pi / count) * i
        x1 = CX + radius * math.cos(angle)
        y1 = CY + radius * math.sin(angle)
        x2 = CX + (radius - length) * math.cos(angle)
        y2 = CY + (radius - length) * math.sin(angle)
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                      f'stroke="{CYAN}" stroke-opacity="{opacity}" stroke-width="1.2"/>')
    return "".join(parts)


def load_logo_as_data_uri(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    if mime is None:
        mime = "image/png"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def build_svg(logo_data_uri: str) -> str:
    r_outer = SIZE * 0.46
    r_mid = SIZE * 0.38
    r_inner = SIZE * 0.30
    r_core = SIZE * 0.18

    logo_x = CX - LOGO_R
    logo_y = CY - LOGO_R
    logo_d = LOGO_R * 2

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" width="{SIZE}" height="{SIZE}" role="img" aria-label="Profile emblem">
  <defs>
    <radialGradient id="core-glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{CYAN_BRIGHT}" stop-opacity="0.9"/>
      <stop offset="60%" stop-color="{CYAN}" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="logo-clip"><circle cx="{CX}" cy="{CY}" r="{LOGO_R}"/></clipPath>
    <filter id="emblem-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2.2" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <style>
      .ring {{ fill: none; stroke: {CYAN_DIM}; stroke-width: 1; }}
      .ring-bright {{ fill: none; stroke: {CYAN}; stroke-width: 1.4; }}
      .spin-slow {{
        transform-box: fill-box; transform-origin: center;
        animation: spin 14s linear infinite;
      }}
      .spin-rev {{
        transform-box: fill-box; transform-origin: center;
        animation: spin-rev 20s linear infinite;
      }}
      @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
      @keyframes spin-rev {{ to {{ transform: rotate(-360deg); }} }}
      .pulse {{
        transform-box: fill-box; transform-origin: center;
        animation: pulse 2.4s ease-in-out infinite;
      }}
      @keyframes pulse {{
        0%, 100% {{ opacity: 0.35; transform: scale(1); }}
        50%      {{ opacity: 0.9;  transform: scale(1.04); }}
      }}
      .fadein {{ opacity: 0; animation: fadein 0.8s ease-out forwards; }}
      @keyframes fadein {{ to {{ opacity: 1; }} }}
    </style>
  </defs>

  <circle cx="{CX}" cy="{CY}" r="{r_outer + 6}" fill="{BG}"/>
  <circle class="pulse" cx="{CX}" cy="{CY}" r="{r_outer}" fill="url(#core-glow)"/>

  <g class="spin-slow">{ticks(r_outer, 48, length=5, opacity=0.35)}</g>
  <g class="spin-rev">{ticks(r_mid, 24, length=6, opacity=0.5)}</g>

  <circle class="ring" cx="{CX}" cy="{CY}" r="{r_outer}"/>
  <circle class="ring-bright" cx="{CX}" cy="{CY}" r="{r_inner}"/>
  <circle class="ring" cx="{CX}" cy="{CY}" r="{r_core}"/>

  <g class="spin-slow">
    <circle cx="{CX + r_mid}" cy="{CY}" r="2.6" fill="{CYAN_BRIGHT}"/>
  </g>

  <g filter="url(#emblem-glow)" class="fadein" style="animation-delay:0.3s">
    <image href="{logo_data_uri}" x="{logo_x}" y="{logo_y}" width="{logo_d}" height="{logo_d}"
           clip-path="url(#logo-clip)" preserveAspectRatio="xMidYMid slice"/>
  </g>
</svg>
'''
    return svg


def main():
    path = sys.argv[1] if len(sys.argv) >= 2 else DEFAULT_LOGO_PATH
    if not os.path.exists(path):
        print(f"Logo not found at: {path}")
        print('Usage: python scripts/make_emblem_svg.py "path\\to\\your-logo.png"')
        sys.exit(1)

    logo_data_uri = load_logo_as_data_uri(path)
    svg = build_svg(logo_data_uri)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main() 