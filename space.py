import requests
from datetime import datetime
import os

USERNAME = os.getenv("GITHUB_USERNAME", "juniorschmitz")
TOKEN = os.getenv("GITHUB_TOKEN")

GRAPHQL_API_URL = "https://api.github.com/graphql"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

SVG_HEADER = """<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' width='900' height='180' style='background:black;font-family:monospace;font-size:14px;'>"""
SVG_FOOTER = "</svg>"

INVADER = "👾"
SHIP = "🚀"


def get_contributions():
    query = f"""
    query {{
      user(login: \"{USERNAME}\") {{
        contributionsCollection {{
          contributionCalendar {{
            totalContributions
            weeks {{
              contributionDays {{
                date
                contributionCount
              }}
            }}
          }}
        }}
      }}
    }}
    """
    response = requests.post(GRAPHQL_API_URL, json={"query": query}, headers=HEADERS)
    data = response.json()
    weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    days = []
    for week in weeks:
        for day in week['contributionDays']:
            days.append({
                'date': day['date'],
                'count': day['contributionCount']
            })
    return days


def draw_svg(contributions):
    lines = [SVG_HEADER]
    cell_size = 14
    padding = 2
    x_start = 100
    y_start = 20
    ship_x = 30

    active_cells = []

    for i, day in enumerate(contributions):
        col = i // 7
        row = i % 7
        y = y_start + row * (cell_size + padding)
        x = x_start + col * (cell_size + padding)

        count = day['count']
        alien_id = f"invader{i}"

        # base: célula como fundo do grid
        base_color = "#222"  # fundo escuro
        lines.append(f"<rect x='{x}' y='{y - 12}' width='{cell_size}' height='{cell_size}' fill='{base_color}' rx='2' />")

        if count > 0:
            lines.append(f"<text id='{alien_id}' x='{x}' y='{y}' fill='violet'>")
            lines.append(f"  {INVADER}")
            lines.append(f"  <animate attributeName='y' values='{y};{y+3};{y}' dur='0.6s' repeatCount='indefinite' />")
            lines.append("</text>")
            active_cells.append((x, y, alien_id))

    # Nave fixa à esquerda
    lines.append(f"<text x='{ship_x}' y='90' fill='white'>{SHIP}</text>")

    # Tiros animados apenas para alienígenas reais
    for idx, (x, y, alien_id) in enumerate(active_cells):
        delay = idx * 1.5
        lines.append(f"<line x1='{ship_x + 10}' y1='95' x2='{x}' y2='{y}' stroke='yellow' stroke-width='1' visibility='hidden'>")
        lines.append(f"  <set attributeName='visibility' to='visible' begin='{delay}s' dur='0.7s' />")
        lines.append(f"  <animate attributeName='x2' values='{ship_x + 10};{x}' begin='{delay}s' dur='0.7s' fill='freeze' />")
        lines.append("</line>")

        # Invisibilizar alien após impacto
        lines.append(f"<use xlink:href='#{alien_id}'>")
        lines.append(f"  <set attributeName='visibility' to='hidden' begin='{delay + 0.7}s' />")
        lines.append("</use>")

    lines.append(f"<text x='30' y='175' fill='white'>{USERNAME}</text>")
    lines.append(SVG_FOOTER)
    return "\n".join(lines)


def save_svg(content, path="output/space-invaders-grid.svg"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    contributions = get_contributions()
    svg_content = draw_svg(contributions)
    save_svg(svg_content)
    print("✅ Grade completa com alienígenas baseada no gráfico de contribuições gerada com sucesso!")
