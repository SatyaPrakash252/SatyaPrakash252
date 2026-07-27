#!/usr/bin/env python3
"""
Fetches the public contribution calendar for GITHUB_USERNAME from
https://github.com/users/<username>/contributions (no auth, no token —
it's the same public fragment the profile page itself loads) and writes
data/contributions.json with the raw day grid plus derived stats
(current streak, longest streak, best day, total).
"""

import os
import re
import json
import sys
from datetime import date, datetime, timezone

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_USERNAME", "SatyaPrakash252")
OUT_PATH = os.environ.get("CONTRIB_OUT", "data/contributions.json")

URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch_html() -> str:
    r = requests.get(URL, timeout=15, headers={"User-Agent": "profile-readme-bot"})
    r.raise_for_status()
    return r.text


def parse(html: str):
    soup = BeautifulSoup(html, "html.parser")

    # tooltip text ("3 contributions on August 3rd." / "No contributions on ...")
    # is a sibling <tool-tip for="cell-id">, keyed by the cell's id.
    tooltip_by_id = {}
    for tip in soup.select("tool-tip"):
        target = tip.get("for")
        if target:
            tooltip_by_id[target] = tip.get_text(strip=True)

    count_re = re.compile(r"^(No|\d+)\s+contribution")

    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        cell_id = td.get("id", "")
        m = re.search(r"contribution-day-component-(\d+)-(\d+)", cell_id)
        if not m or not td.get("data-date"):
            continue
        row, col = int(m.group(1)), int(m.group(2))
        level = int(td.get("data-level", 0))

        count = 0
        tip_text = tooltip_by_id.get(cell_id, "")
        cm = count_re.match(tip_text)
        if cm and cm.group(1) != "No":
            count = int(cm.group(1))

        days.append({
            "date": td["data-date"],
            "level": level,
            "count": count,
            "row": row,
            "col": col,
        })

    days.sort(key=lambda d: d["date"])

    total_match = re.search(r"([\d,]+)\s*\n?\s*contributions?\s+in the last year", soup.get_text())
    total = int(total_match.group(1).replace(",", "")) if total_match else sum(d["count"] for d in days)

    return days, total


def compute_stats(days, total):
    current_streak = 0
    longest_streak = 0
    running = 0
    today = date.today().isoformat()

    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    # current streak counts back from the most recent day that has data
    for d in reversed(days):
        if d["date"] > today:
            continue
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    best_day = max(days, key=lambda d: d["count"]) if days else None

    return {
        "total_last_year": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
    }


def main():
    try:
        html = fetch_html()
        days, total = parse(html)
        if not days:
            raise ValueError("parsed zero contribution cells — GitHub markup may have changed")
        stats = compute_stats(days, total)
    except Exception as e:  # noqa: BLE001
        print(f"::warning::Could not refresh contributions, keeping existing data.json. ({e})", file=sys.stderr)
        sys.exit(0)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "username": USERNAME,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "days": days,
            "stats": stats,
        }, f, indent=2)

    print(f"Wrote {OUT_PATH}: {len(days)} days, total={stats['total_last_year']}, "
          f"current_streak={stats['current_streak']}, longest_streak={stats['longest_streak']}")


if __name__ == "__main__":
    main()
