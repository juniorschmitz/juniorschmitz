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

SVG_HEADER = """<svg xmlns='http://www.w3.org/2000/svg' width='800' height='180' style='background:black;font-family:monospace;font-size:14px;'>"""
SVG_FOOTER = "</svg>"

INVADER = "👾"
SHIP = "🚀"


def get_contributions():
    query = f"""
    query {{
      user(login: \"{USERNAME}\") {{
        contributionsCollection {{
          contributionCalendar {{
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
    x_start = 30
    y_start = 20
    ship_y = 150

    active_cells = []

    for i, day in enumerate(contributions):
        x = x_start + (i // 7) * (cell_size + padding)
        y = y_start + (i % 7) * (cell_size + padding)

        count = day['count']
        if count > 0:
            lines.append(f"<text x='{x}' y='{y}' fill='violet'>")
            lines.append(f"  {INVADER}")
            lines.append(f"  <animate attributeName='y' values='{y};{y+3};{y}' dur='0.6s' repeatCount='indefinite' />")
            lines.append("</text>")
            active_cells.append((x, y))

    # Nave animada
    if active_cells:
        path_x = ";".join(str(x) for x, _ in active_cells)
        path_y = ";".join(str(ship_y - 5 + (i % 3) * 5) for i in range(len(active_cells)))

        lines.append(f"<text x='{active_cells[0][0]}' y='{ship_y}' fill='white'>")
        lines.append(f"  {SHIP}")
        lines.append(f"  <animate attributeName='x' values='{path_x}' dur='8s' repeatCount='indefinite' />")
        lines.append(f"  <animate attributeName='y' values='{path_y}' dur='2s' repeatCount='indefinite' />")
        lines.append("</text>")

        # Disparos animados
        for idx, (x, y) in enumerate(active_cells):
            shot_dur = 1 + (idx % 3) * 0.5
            lines.append(f"<line x1='{x + 5}' y1='{ship_y - 10}' x2='{x + 5}' y2='{y}' stroke='yellow' stroke-width='1'>")
            lines.append(f"  <animate attributeName='y1' values='{ship_y - 10};{y}' dur='{shot_dur}s' repeatCount='indefinite' />")
            lines.append(f"  <animate attributeName='y2' values='{y};{y - 10};{y}' dur='{shot_dur}s' repeatCount='indefinite' />")
            lines.append("</line>")

    lines.append(f"<text x='30' y='175' fill='white'>{USERNAME}</text>")
    lines.append(SVG_FOOTER)
    return "\n".join(lines)


def save_svg(content, path="output/space-invaders-grid.svg"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


if __name__ == "__main__":
    contributions = get_contributions()
    svg_content = draw_svg(contributions)
    save_svg(svg_content)
    print("✅ SVG com nave e tiros animados gerado com sucesso!")
