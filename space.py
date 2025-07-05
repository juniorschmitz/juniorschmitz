# space_invaders_generator.py (versão baseada no contribution graph)

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

SVG_HEADER = """<svg xmlns='http://www.w3.org/2000/svg' width='800' height='160' style='background:black;font-family:monospace;font-size:14px;'>"""
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
    
    for i, day in enumerate(contributions):
        x = x_start + (i // 7) * (cell_size + padding)
        y = y_start + (i % 7) * (cell_size + padding)
        
        count = day['count']
        if count > 0:
            lines.append(f"<text x='{x}' y='{y}' fill='violet'>")
            lines.append(f"  {INVADER}")
            lines.append(f"  <animate attributeName='y' values='{y};{y+3};{y}' dur='0.6s' repeatCount='indefinite' />")
            lines.append("</text>")

    # Nave (última posição com contribuições)
    lines.append(f"<text x='{x_start + ((len(contributions)//2)//7)*(cell_size+padding)}' y='145' fill='white'>{SHIP}</text>")
    lines.append(f"<text x='30' y='155' fill='white'>{USERNAME}</text>")
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
    print("✅ SVG atualizado com dados do contribution graph!")
