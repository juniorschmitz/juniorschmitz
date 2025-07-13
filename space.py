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

    # Timings corrigidos
    move_duration = 0.8      # Tempo para nave se mover
    shot_duration = 0.6      # Tempo para tiro viajar
    explosion_duration = 0.5 # Tempo de explosão
    cycle_interval = 2.0     # Intervalo entre ataques
    
    total_duration = len(contributions) * cycle_interval
    ciclos = 2

    # Grid de fundo
    for i in range(53 * 7):
        col, row = divmod(i, 7)
        x = x_start + col * (cell_size + padding)
        y = y_start + row * (cell_size + padding)
        lines.append(f"<rect x='{x}' y='{y - 12}' width='{cell_size}' height='{cell_size}' fill='#222' rx='2'/>")

    # Nave principal
    lines.append(f"<text id='ship' x='{ship_x}' y='{ship_y_default}' fill='white'>{SHIP}</text>")

    for ciclo in range(ciclos):
        ciclo_offset = ciclo * total_duration

        for idx, (cell_idx, _) in enumerate(contributions):
            delay = ciclo_offset + idx * cycle_interval
            
            col, row = divmod(cell_idx, 7)
            alien_x = x_start + col * (cell_size + padding)
            alien_y = y_start + row * (cell_size + padding)

            # Timings sincronizados
            move_start = delay
            move_end = move_start + move_duration
            shot_start = move_end  # Tiro começa quando nave chega na posição
            shot_end = shot_start + shot_duration
            explosion_start = shot_end  # Explosão começa quando tiro atinge alien
            explosion_end = explosion_start + explosion_duration
            return_start = explosion_end  # Nave retorna após explosão
            
            reset_time = (ciclo + 1) * total_duration

            # Alien com animação de movimento no lugar
            alien_id = f"alien_{ciclo}_{idx}"
            lines.append(f"<text id='{alien_id}' x='{alien_x}' y='{alien_y}' fill='violet' opacity='1'>")
            lines.append(f"{INVADER}")
            # Animação de movimento lateral no lugar (para até o momento da explosão)
            lines.append(f"<animate attributeName='x' values='{alien_x};{alien_x+5};{alien_x};{alien_x-5};{alien_x}' dur='1.5s' "
                         f"begin='{ciclo_offset}s' repeatCount='indefinite'/>")
            # Animação de movimento vertical (hover)
            lines.append(f"<animate attributeName='y' values='{alien_y};{alien_y+3};{alien_y};{alien_y-2};{alien_y}' dur='1.2s' "
                         f"begin='{ciclo_offset + 0.3}s' repeatCount='indefinite'/>")
            # DESAPARECIMENTO TOTAL - usar opacity em vez de visibility
            lines.append(f"<animate attributeName='opacity' values='1;1;0' dur='0.1s' "
                         f"begin='{explosion_start}s' fill='freeze'/>")
            # Alien só reaparece no próximo ciclo completo
            if ciclo < ciclos - 1:  # Não reaparece no último ciclo
                lines.append(f"<animate attributeName='opacity' values='0;1' dur='0.1s' "
                             f"begin='{reset_time}s' fill='freeze'/>")
            lines.append("</text>")

            # Explosão sincronizada
            explosion_id = f"explosion_{ciclo}_{idx}"
            lines.append(f"<text id='{explosion_id}' x='{alien_x}' y='{alien_y}' visibility='hidden' font-size='16'>")
            lines.append(EXPLOSION)
            lines.append(f"<set attributeName='visibility' to='visible' begin='{explosion_start}s' dur='{explosion_duration}s'/>")
            lines.append(f"<animate attributeName='opacity' values='1;0.7;1;0.5;1;0' dur='{explosion_duration}s' begin='{explosion_start}s'/>")
            lines.append("</text>")

            # Movimento da nave (apenas vertical - para cima e para baixo)
            lines.append(f"<animate xlink:href='#ship' attributeName='y' "
                         f"values='{ship_y_default};{alien_y};{ship_y_default}' "
                         f"dur='{move_duration + shot_duration + explosion_duration}s' "
                         f"begin='{move_start}s' fill='freeze'/>")

            # Tiro horizontal - da nave até o alien
            lines.append(f"<rect x='{ship_x + 10}' y='{alien_y}' width='6' height='2' fill='yellow' visibility='hidden'>")
            lines.append(f"<set attributeName='visibility' to='visible' begin='{shot_start}s'/>")
            lines.append(f"<animate attributeName='x' from='{ship_x + 10}' to='{alien_x - 3}' begin='{shot_start}s' dur='{shot_duration}s' fill='freeze'/>")
            lines.append(f"<set attributeName='visibility' to='hidden' begin='{shot_end}s'/>")
            lines.append("</rect>")

            # Efeito de flash no impacto
            lines.append(f"<circle cx='{alien_x}' cy='{alien_y}' r='15' fill='white' opacity='0' visibility='hidden'>")
            lines.append(f"<set attributeName='visibility' to='visible' begin='{explosion_start}s' dur='0.1s'/>")
            lines.append(f"<animate attributeName='opacity' values='0;0.8;0' dur='0.1s' begin='{explosion_start}s'/>")
            lines.append("</circle>")

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
    print(f"Space Invaders gerado com {len(contributions)} alvos!")
    print("Arquivo salvo em: output/space-invaders-grid.svg")
