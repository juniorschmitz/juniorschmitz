import requests
import os

USERNAME = os.getenv("GITHUB_USERNAME", "juniorschmitz")
TOKEN = os.getenv("GITHUB_TOKEN")

GRAPHQL_API_URL = "https://api.github.com/graphql"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

SVG_HEADER = """<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'
width='900' height='200' style='background:black;font-family:monospace;font-size:14px;'>"""
SVG_FOOTER = "</svg>"

INVADER = "👾"
SHIP = "🚀"
EXPLOSION = "💥"

def get_contributions():
    query = f"""
    query {{
      user(login: \"{USERNAME}\") {{
        contributionsCollection {{
          contributionCalendar {{
            weeks {{
              contributionDays {{
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
    days = [day for week in weeks for day in week['contributionDays']]
    return [(idx, day['contributionCount']) for idx, day in enumerate(days) if day['contributionCount'] > 0]

def draw_svg(contributions):
    lines = [SVG_HEADER]

    ship_x, ship_y_default = 30, 90
    cell_size, padding = 14, 2
    x_start, y_start = 100, 20

    total_duration = len(contributions) * 2
    ciclos = 2

    # Grid de fundo
    for i in range(53 * 7):
        col, row = divmod(i, 7)
        x = x_start + col * (cell_size + padding)
        y = y_start + row * (cell_size + padding)
        lines.append(f"<rect x='{x}' y='{y - 12}' width='{cell_size}' height='{cell_size}' fill='#222' rx='2'/>")

    lines.append(f"<text id='ship' x='{ship_x}' y='{ship_y_default}' fill='white'>{SHIP}</text>")

    for ciclo in range(ciclos):
        ciclo_offset = ciclo * total_duration

        for idx, (cell_idx, _) in enumerate(contributions):
            delay = ciclo_offset + idx * 1.5
            impact_time = delay + 1.0
            reset_time = (ciclo + 1) * total_duration

            col, row = divmod(cell_idx, 7)
            alien_x = x_start + col * (cell_size + padding)
            alien_y = y_start + row * (cell_size + padding)

            # Alien
            alien_id = f"alien_{ciclo}_{idx}"
            lines.append(f"<text id='{alien_id}' x='{alien_x}' y='{alien_y}' fill='violet' visibility='visible'>")
            lines.append(f"{INVADER}")
            lines.append(f"<animate attributeName='y' values='{alien_y};{alien_y+3};{alien_y}' dur='0.6s' "
                         f"begin='{ciclo_offset}s' repeatCount='indefinite'/>")
            lines.append(f"<set attributeName='visibility' to='hidden' begin='{impact_time}s'/>")
            lines.append(f"<set attributeName='visibility' to='visible' begin='{reset_time}s'/>")
            lines.append("</text>")

            # Explosão
            explosion_id = f"explosion_{ciclo}_{idx}"
            lines.append(f"<text id='{explosion_id}' x='{alien_x}' y='{alien_y}' visibility='hidden' font-size='16'>")
            lines.append(EXPLOSION)
            lines.append(f"<set attributeName='visibility' to='visible' begin='{impact_time}s' dur='0.5s'/>")
            lines.append(f"<set attributeName='visibility' to='hidden' begin='{impact_time + 0.5}s'/>")
            lines.append("</text>")

            # Nave (movimenta primeiro)
            lines.append(f"<animate xlink:href='#ship' attributeName='y' values='{ship_y_default};{alien_y};{ship_y_default}' "
                         f"begin='{delay}s' dur='1s' fill='freeze'/>")

            # Tiro
            tiro_inicio = delay + 1.0
            lines.append(f"<rect x='{ship_x + 10}' y='{alien_y - 1}' width='6' height='2' fill='yellow' visibility='hidden'>")
            lines.append(f"<set attributeName='visibility' to='visible' begin='{tiro_inicio}s'/>")
            lines.append(f"<animate attributeName='x' from='{ship_x + 10}' to='{alien_x}' begin='{tiro_inicio}s' dur='0.4s' fill='freeze'/>")
            lines.append(f"<set attributeName='visibility' to='hidden' begin='{tiro_inicio + 0.4}s'/>")
            lines.append("</rect>")

    # Loop infinito (reset silencioso)
    lines.append(f"<rect visibility='hidden'>")
    lines.append(f"<set attributeName='visibility' to='visible' begin='{total_duration * ciclos}s' dur='0.1s' "
                 f"repeatCount='indefinite'/>")
    lines.append("</rect>")

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
