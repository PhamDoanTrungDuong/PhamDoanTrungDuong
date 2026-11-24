"""Turns a picture into the ASCII portrait on the profile card (run by hand, once).

    python make_ascii.py                 -> ascii.txt from the GitHub avatar
    python make_ascii.py picture.jpg     -> ascii.txt from that picture
"""
import io
import sys
import urllib.request

from PIL import Image, ImageOps

AVATAR = "https://avatars.githubusercontent.com/u/76588259?v=4"
COLS, ROWS = 52, 34  # drawn at 12 px with 15 px lines: cells about twice as tall as wide
RAMP = " .:-=+*#%@"  # light to dark; drawn light-on-dark, so dense characters are the bright parts

raw = open(sys.argv[1], "rb").read() if len(sys.argv) > 1 else urllib.request.urlopen(AVATAR, timeout=30).read()
img = Image.open(io.BytesIO(raw)).convert("L")
# Cut to the cell shape (COLS wide, ROWS twice-tall cells high) from the top, where the face is.
w, h = img.size
want = COLS / (ROWS * 2)
crop_w = min(w, int(h * want))
crop_h = min(h, int(crop_w / want))
img = img.crop(((w - crop_w) // 2, 0, (w + crop_w) // 2, crop_h))
# Stretch the tones, then lift the dark mid-tones a little so a dim face reads (the background stays dark).
img = ImageOps.autocontrast(img, cutoff=(15, 0.5)).point(lambda v: int(255 * (v / 255) ** 0.55))
img = img.resize((COLS, ROWS), Image.LANCZOS)
lines = []
for y in range(ROWS):
    row = ""
    for x in range(COLS):
        v = img.getpixel((x, y)) / 255  # 0 dark .. 1 bright
        row += RAMP[min(len(RAMP) - 1, int(v * len(RAMP)))]
    lines.append(row.rstrip())
open("ascii.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
