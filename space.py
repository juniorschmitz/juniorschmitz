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
    print(f"🔍 Total de dias carregados: {len(days)}")
    return days


def draw_svg(contributions):
    lines = [SVG_HEADER]
    cell_size = 14
    padding = 2
    x_start = 100
    y_start = 20
    ship_x = 30
    ship_y_default = 90

    active_cells = []

    # Definir alienígenas como símbolos reutilizáveis
    for i, day in enumerate(contributions):
        col = i // 7
        row = i % 7
        y = y_start + row * (cell_size + padding)
        x = x_start + col * (cell_size + padding)

        count = day['count']
        alien_id = f"invader{i}"

        base_color = "#222"
        lines.append(f"<rect x='{x}' y='{y - 12}' width='{cell_size}' height='{cell_size}' fill='{base_color}' rx='2' />")

        if count > 0:
            lines.append(f"<g id='{alien_id}'>")
            lines.append(f"  <text x='0' y='0' fill='violet'>")
            lines.append(f"    {INVADER}")
            lines.append(f"    <animate attributeName='y' values='0;3;0' dur='0.6s' repeatCount='indefinite' />")
            lines.append("  </text>")
            lines.append("</g>")
            active_cells.append((x, y, alien_id, i))

    # Nave única
    lines.append(f"<text id='ship' x='{ship_x}' y='{ship_y_default}' fill='white'>{SHIP}</text>")

    tiro_duracao = 0.4
    for idx, (target_x, target_y, alien_id, cell_index) in enumerate(active_cells):
        delay = idx * 1.5
        impact_time = delay + tiro_duracao

        # Mover nave até alien
        lines.append(f"<animate xlink:href='#ship' attributeName='y' values='{ship_y_default};{target_y}' begin='{delay}s' dur='0.4s' fill='freeze' />")

        # Tiro como retângulo animado
        x1 = ship_x + 10
        x2 = target_x
        y = target_y
        lines.append(f"<rect id='bullet{idx}' x='{x1}' y='{y - 1}' width='6' height='2' fill='yellow' visibility='hidden'>")
        lines.append(f"  <set attributeName='visibility' to='visible' begin='{delay + 0.4}s' dur='{tiro_duracao}s' />")
        lines.append(f"  <animate attributeName='x' from='{x1}' to='{x2}' begin='{delay + 0.4}s' dur='{tiro_duracao}s' fill='freeze' />")
        lines.append(f"  <set attributeName='visibility' to='hidden' begin='{delay + tiro_duracao + 0.6}s' />")
        lines.append("</rect>")

        # Inserir alienígena como <use> para permitir remoção
        lines.append(f"<use xlink:href='#{alien_id}' x='{target_x}' y='{target_y}'>")
        lines.append(f"  <set attributeName='visibility' to='hidden' begin='{impact_time + 0.4}s' />")
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
    print("✅ Tiro animado como bala + alienígenas desaparecendo corretamente com <use>!")
