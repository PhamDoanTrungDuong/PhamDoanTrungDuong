"""Draws the profile card (dark_mode.svg and light_mode.svg): the ASCII portrait on the left and a
neofetch-style list on the right, with GitHub numbers read fresh each run.

    GITHUB_TOKEN=... python generate.py      (the token only raises the rate limit; public data)
"""
import datetime
import html
import json
import os
import urllib.request

USER = "PhamDoanTrungDuong"
JOINED = datetime.date(2020, 12, 25)  # when this GitHub account was made

# (key, value) rows; None is a blank line, a str alone is a section heading.
ABOUT = [
    ("OS", "Windows 11"),
    ("On GitHub", None),  # filled in: time since JOINED
    None,
    ("Languages.Programming", "C#, TypeScript, JavaScript, Rust"),
    ("Languages.Also", "Python, Dart, PHP"),
    ("Languages.Web", "HTML, CSS, Tailwind"),
    ("Frameworks", "ASP.NET, React, Vue, Flutter"),
    ("Languages.Real", "Vietnamese"),
    None,
    ("Now building", "Dynamik, a notch for Windows (Rust)"),
    ("Learning", "C#"),
    ("Ask me about", "React, ASP.NET"),
    None,
    "Contact",
    ("Email", "pdtduong@gmail.com"),
    ("Facebook", "trungduong212"),
    ("Instagram", "_trungduong"),
    None,
    "GitHub Stats",
]

THEMES = {
    "dark_mode.svg": dict(bg="#161b22", text="#c9d1d9", key="#ffa657", value="#a5d6ff", dots="#616e7f", art="#c9d1d9", head="#c9d1d9"),
    "light_mode.svg": dict(bg="#f6f8fa", text="#24292f", key="#953800", value="#0a3069", dots="#c2cfde", art="#24292f", head="#24292f"),
}
WIDTH = 985
LINE = 20  # px between rows
ART_FONT, ART_LINE = 12, 15  # the portrait is drawn smaller, for more detail
COL = 58  # characters from the start of a row to where its value ends (dot leaders fill the gap)


def api(path):
    req = urllib.request.Request("https://api.github.com" + path, headers={"Accept": "application/vnd.github+json", "User-Agent": USER})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def stats():
    user = api(f"/users/{USER}")
    repos, page = [], 1
    while True:
        batch = api(f"/users/{USER}/repos?per_page=100&page={page}&type=owner")
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    own = [r for r in repos if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in own)
    commits = api(f"/search/commits?q=author:{USER}&per_page=1")["total_count"]
    return dict(repos=user["public_repos"], own=len(own), stars=stars, commits=commits, followers=user["followers"])


def since(start, today):
    """'5 years, 10 months, 30 days' from start to today."""
    years = today.year - start.year - ((today.month, today.day) < (start.month, start.day))
    months = (today.month - start.month - (today.day < start.day)) % 12
    anchor = datetime.date(start.year + years + (start.month + months - 1) // 12, (start.month + months - 1) % 12 + 1, 1)
    days = (today - anchor.replace(day=min(start.day, 28))).days
    unit = lambda n, w: f"{n} {w}{'' if n == 1 else 's'}"
    return f"{unit(years, 'year')}, {unit(months, 'month')}, {unit(days, 'day')}"


def row(key, value, c):
    """One neofetch row: '. Key: ....... value' with the dots filling to COL."""
    dots = max(1, COL - len(key) - len(value) - 4)
    return (f'<tspan fill="{c["text"]}">. </tspan><tspan fill="{c["key"]}">{html.escape(key)}</tspan>'
            f'<tspan fill="{c["text"]}">:</tspan><tspan fill="{c["dots"]}"> {"." * dots} </tspan>'
            f'<tspan fill="{c["value"]}">{html.escape(value)}</tspan>')


def card(c, numbers, art, today):
    rows = [f'<tspan fill="{c["head"]}">trungduong</tspan><tspan fill="{c["text"]}">@github</tspan>'
            f'<tspan fill="{c["text"]}"> {"—" * (COL - 18)}</tspan>']
    for item in ABOUT:
        if item is None:
            rows.append(f'<tspan fill="{c["text"]}">.</tspan>')
        elif isinstance(item, str):
            rows.append(f'<tspan fill="{c["head"]}">- {html.escape(item)} </tspan><tspan fill="{c["text"]}">{"—" * (COL - len(item) - 3)}</tspan>')
        else:
            key, value = item
            rows.append(row(key, value if value is not None else since(JOINED, today), c))
    n = numbers
    rows.append(row("Repos", f"{n['repos']} (own {n['own']})", c))
    rows.append(row("Stars", str(n["stars"]), c))
    rows.append(row("Commits", f"{n['commits']:,}", c))
    rows.append(row("Followers", str(n["followers"]), c))
    height = max(len(rows) * LINE, len(art) * ART_LINE) + 40
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,\'Courier New\',monospace" width="{WIDTH}px" height="{height}px" font-size="16px">',
           f'<rect width="{WIDTH}px" height="{height}px" fill="{c["bg"]}" rx="15"/>',
           f'<text x="15" y="30" fill="{c["art"]}" font-size="{ART_FONT}px" class="ascii" xml:space="preserve">']
    out += [f'<tspan x="15" y="{30 + i * ART_LINE}">{html.escape(line)}</tspan>' for i, line in enumerate(art)]
    out.append("</text>")
    out.append(f'<text x="390" y="30" fill="{c["text"]}" xml:space="preserve">')
    out += [f'<tspan x="390" y="{30 + i * LINE}">{r}</tspan>' for i, r in enumerate(rows)]
    out += ["</text>", "</svg>"]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    art = open("ascii.txt", encoding="utf-8").read().rstrip("\n").split("\n")
    numbers = stats()
    today = datetime.date.today()
    # ascii.txt is drawn for a dark card (dense = bright); the light card swaps dense and sparse.
    ramp = " .:-=+*#%@"
    flip = str.maketrans(ramp, ramp[::-1])
    width = max(len(line) for line in art)
    light_art = [line.ljust(width).translate(flip) for line in art]
    for name, colours in THEMES.items():
        open(name, "w", encoding="utf-8").write(card(colours, numbers, light_art if name.startswith("light") else art, today))
    print(numbers)
