import requests
import os

USERNAME = os.getenv("GITHUB_USERNAME", "juniorschmitz")
TOKEN = os.getenv("GITHUB_TOKEN")

GRAPHQL_API_URL = "https://api.github.com/graphql"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

SVG_HEADER = """<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' width='900' height='200' style='background:black;font-family:monospace;font-size:14px;'>"""
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
    }}"""

    response = requests.post(GRAPHQL_API_URL, json={"query": query}, headers=HEADERS)
    data = response.json()

    weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    days = []
    for week in weeks:
        for day in week['contributionDays']:
            days.append({'date': day['date'], 'count': day['contributionCount']})
    return days


def draw_svg(contributions):
    lines = [SVG_HEADER]
    cell_size, padding = 14, 2
    x_start, y_start = 100, 20
    ship_x, ship_y_default = 30, 90

    active_cells = [(x_start + (i // 7)*(cell_size+padding), y_start + (i % 7)*(cell_size+padding))
                    for i, day in enumerate(contributions) if day['count'] > 0]

    for i in range(len(contributions)):
        col, row = i // 7, i % 7
        y, x = y_start + row*(cell_size+padding), x_start + col*(cell_size+padding)
        lines.append(f"<rect x='{x}' y='{y - 12}' width='{cell_size}' height='{cell_size}' fill='#222' rx='2' />")

    lines.append(f"<text id='ship' x='{ship_x}' y='{ship_y_default}' fill='white'>{SHIP}</text>")

    total_duration = len(active_cells) * 1.5

    for idx, (target_x, target_y) in enumerate(active_cells):
        delay, impact = idx * 1.5, idx * 1.5 + 0.4

        lines.append(f"<text id='alien_{idx}' x='{target_x}' y='{target_y}' fill='violet' visibility='visible'>")
        lines.append(f"  {INVADER}")
        lines.append(f"  <animate attributeName='y' values='{target_y};{target_y+3};{target_y}' dur='0.6s' repeatCount='indefinite'/>")
        lines.append(f"  <animateTransform attributeName='transform' attributeType='XML' type='scale' values='1;1.8;0' dur='0.3s' begin='{impact}s' fill='freeze'/>")
        lines.append(f"  <set attributeName='visibility' to='hidden' begin='{impact + 0.3}s'/>")
        lines.append(f"  <set attributeName='visibility' to='visible' begin='{total_duration + 1}s'/>")
        lines.append("</text>")

        lines.append(f"<animate xlink:href='#ship' attributeName='y' values='{ship_y_default};{target_y};{ship_y_default}' begin='{delay}s' dur='1s' fill='freeze'/>")

        lines.append(f"<rect x='{ship_x+10}' y='{target_y-1}' width='6' height='2' fill='yellow' visibility='hidden'>")
        lines.append(f"  <set attributeName='visibility' to='visible' begin='{impact-0.4}s' dur='0.4s'/>")
        lines.append(f"  <animate attributeName='x' from='{ship_x+10}' to='{target_x}' begin='{impact-0.4}s' dur='0.4s' fill='freeze'/>")
        lines.append(f"  <set attributeName='visibility' to='hidden' begin='{impact + 0.1}s'/>")
        lines.append("</rect>")

    lines.append(f"<animate id='loop' attributeName='visibility' values='visible' dur='{total_duration + 2}s' repeatCount='indefinite'/>")
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
