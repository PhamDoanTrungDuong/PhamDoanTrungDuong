"""Turns the GitHub avatar into the ASCII portrait on the profile card (run by hand, once).

    python make_ascii.py            -> ascii.txt
"""
import io
import urllib.request

from PIL import Image, ImageOps

AVATAR = "https://avatars.githubusercontent.com/u/76588259?v=4"
COLS, ROWS = 38, 25  # monospace cells are about twice as tall as wide
RAMP = " .:-=+*#%@"  # light to dark; drawn light-on-dark, so dense characters are the bright parts

raw = urllib.request.urlopen(AVATAR, timeout=30).read()
img = Image.open(io.BytesIO(raw)).convert("L")
img = ImageOps.autocontrast(img, cutoff=2).resize((COLS, ROWS), Image.LANCZOS)
lines = []
for y in range(ROWS):
    row = ""
    for x in range(COLS):
        v = img.getpixel((x, y)) / 255  # 0 dark .. 1 bright
        row += RAMP[min(len(RAMP) - 1, int(v * len(RAMP)))]
    lines.append(row.rstrip())
open("ascii.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
