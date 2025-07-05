# space_invaders_generator.py
# Gera um SVG estilo Space Invaders baseado no número de commits

import requests
from datetime import datetime, timedelta
import os

USERNAME = os.getenv("GITHUB_USERNAME", "juniorschmitz")
TOKEN = os.getenv("GITHUB_TOKEN")

API_URL = f"https://api.github.com/users/{USERNAME}/events"
HEADERS = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

# Cores e dimensões
ENEMY = "👾"
SHIP = "🚀"
BLOCK = "🟪"

SVG_HEADER = """<svg xmlns='http://www.w3.org/2000/svg' width='600' height='400' style='background:black;font-family:monospace;font-size:20px;'>"""
SVG_FOOTER = "</svg>"

def fetch_commit_days():
    resp = requests.get(API_URL, headers=HEADERS)
    events = resp.json()
    commit_days = set()
    for e in events:
        if e["type"] == "PushEvent":
            dt = datetime.strptime(e["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            commit_days.add(dt.date())
    return commit_days

def draw_svg(commit_days):
    lines = [SVG_HEADER]

    # Invasores (dias com commits)
    today = datetime.utcnow().date()
    for i in range(5):
        for j in range(10):
            day = today - timedelta(days=i * 10 + j)
            if day in commit_days:
                x = 30 + j * 50
                y = 30 + i * 40
                lines.append(f"<text x='{x}' y='{y}' fill='lime'>{ENEMY}</text>")

    # Nave do jogador
    lines.append("<text x='270' y='380' fill='white'>🚀</text>")
    lines.append(f"<text x='250' y='395' fill='white'>{USERNAME}</text>")

    # Escudos
    lines.append(f"<text x='150' y='350' fill='violet'>{BLOCK} Tests</text>")
    lines.append(f"<text x='350' y='350' fill='violet'>{BLOCK} CI/CD</text>")

    lines.append(SVG_FOOTER)
    return "\n".join(lines)

def save_svg(content, path="output/space-invaders-grid.svg"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

if __name__ == "__main__":
    commit_days = fetch_commit_days()
    svg_content = draw_svg(commit_days)
    save_svg(svg_content)
    print("✅ SVG gerado com sucesso!")
