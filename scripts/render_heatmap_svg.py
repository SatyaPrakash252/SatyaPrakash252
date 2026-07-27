#!/usr/bin/env python3
"""
Renders data/contributions.json into contrib-heatmap.svg: the classic
53-week x 7-day GitHub contribution grid, drawn as rounded boxes that
slide/fade in diagonally once on load (no infinite loop), followed by a
small stats footer.
"""

import os
import json
import html
import sys

IN_PATH = os.environ.get("CONTRIB_OUT", "data/contributions.json")
OUT_PATH = os.environ.get("HEATMAP_OUT", "assets/contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

CELL = 11
GAP = 3
PAD_L = 28
PAD_T = 34
PAD_R = 16
PAD_B = 44
MONTH_LABEL_H = 14

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def month_labels(days):
    """Return {col: 'Jan'} for the first column each new month appears in."""
    labels = {}
    seen_months = set()
    for d in sorted(days, key=lambda x: x["col"]):
        month = d["date"][:7]  # YYYY-MM
        if month not in seen_months:
            seen_months.add(month)
            mm = int(d["date"][5:7])
            labels[d["col"]] = MONTH_NAMES[mm - 1]
    return labels


def build_svg(data: dict) -> str:
    days = data["days"]
    stats = data["stats"]
    username = data.get("username", "")

    n_cols = max(d["col"] for d in days) + 1
    width = PAD_L + n_cols * (CELL + GAP) + PAD_R
    height = PAD_T + 7 * (CELL + GAP) + PAD_B

    labels = month_labels(days)
    label_svg = []
    for col, name in labels.items():
        x = PAD_L + col * (CELL + GAP)
        label_svg.append(f'<text class="month" x="{x}" y="{PAD_T - 8}">{name}</text>')

    cells = []
    for d in days:
        x = PAD_L + d["col"] * (CELL + GAP)
        y = PAD_T + d["row"] * (CELL + GAP)
        color = PALETTE[min(d["level"], len(PALETTE) - 1)]
        delay = round((d["col"] * 7 + d["row"]) * 0.006, 3)
        title = html.escape(f'{d["count"]} contributions on {d["date"]}')
        cells.append(
            f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
            f'fill="{color}" style="animation-delay:{delay}s"><title>{title}</title></rect>'
        )

    legend_x = width - PAD_R - (len(PALETTE) * (CELL + 3)) - 40
    legend_y = height - 16
    legend_swatches = "".join(
        f'<rect x="{legend_x + 40 + i * (CELL + 3)}" y="{legend_y - CELL + 3}" '
        f'width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>'
        for i, c in enumerate(PALETTE)
    )

    total = stats.get("total_last_year", 0)
    streak = stats.get("current_streak", 0)
    longest = stats.get("longest_streak", 0)
    footer = (f'{total} contributions in the last year &#160;&#183;&#160; '
              f'current streak {streak}d &#160;&#183;&#160; longest streak {longest}d')

    n_cells = len(days)
    total_anim_s = round(n_cells * 0.006 + 0.5, 2)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="Contribution heatmap for {html.escape(username)}">
  <defs>
    <style>
      .bg {{ fill: #0d1117; }}
      .month {{ font-family: -apple-system, Segoe UI, Helvetica, Arial, sans-serif; font-size: 10px; fill: #8b949e; }}
      .legend-text {{ font-family: -apple-system, Segoe UI, Helvetica, Arial, sans-serif; font-size: 10px; fill: #8b949e; }}
      .footer {{ font-family: -apple-system, Segoe UI, Helvetica, Arial, sans-serif; font-size: 11px; fill: #c9d1d9; }}
      .cell {{
        opacity: 0;
        transform-box: fill-box;
        transform-origin: center;
        transform: scale(0.4);
        animation: pop 0.5s ease-out forwards;
      }}
      @keyframes pop {{
        0%   {{ opacity: 0; transform: scale(0.4); }}
        70%  {{ opacity: 1; transform: scale(1.08); }}
        100% {{ opacity: 1; transform: scale(1); }}
      }}
    </style>
  </defs>
  <rect class="bg" x="0" y="0" width="{width}" height="{height}" rx="10"/>
  {''.join(label_svg)}
  {''.join(cells)}
  <text class="legend-text" x="{legend_x}" y="{legend_y}">Less</text>
  {legend_swatches}
  <text class="legend-text" x="{legend_x + 40 + len(PALETTE) * (CELL + 3) + 6}" y="{legend_y}">More</text>
  <text class="footer" x="{PAD_L}" y="{height - 16}">{footer}</text>
</svg>
'''
    return svg


def main():
    if not os.path.exists(IN_PATH):
        print(f"::warning::{IN_PATH} not found, skipping heatmap render.", file=sys.stderr)
        sys.exit(0)
    with open(IN_PATH, encoding="utf-8") as f:
        data = json.load(f)

    svg = build_svg(data)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
