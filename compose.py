#!/usr/bin/env python3
"""Build entry.png for the news-image-20261124 entry (v4).

The four story illustrations live in ../news-image/panels (drawn in-session for
this day's news). This script composes them into one 1024x1024 newspaper front
page with crisp PIL text.

v4 (after round 2 judged v3 at rank 8,207 of 9,063, 32.36% — up only 3.42
points from v2's 28.94%): the legibility fix helped a little, so the remaining
problem is the format itself — a busy four-panel collage whose AI illustrations
are generic and do not depict the events. v4 changes the composition
radically: ONE dominant image (the lead story), one giant headline, and the
other three stories as large text-only lines. No small images, no sublines, no
clutter — a single clear composition that reads at the judge's ~300 px width.
Every headline is at least 36 px (about 11 px at 300 px). Output is JPEG bytes
in a file named entry.png (the bounty rules allow PNG or JPEG bytes under that
name), 1024x1024 and under 1 MiB.
"""
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os

PANELS = '/home/hatch/workspace/makefun/news-image/panels'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'entry.png')

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (18, 18, 18)
RED = (163, 29, 29)
RULE = (40, 40, 40)

SERIF_B = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
SANS_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def font(path, size):
    return ImageFont.truetype(path, size)

def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def fit(path, tw, th):
    im = Image.open(path).convert('RGB')
    return ImageOps.fit(im, (tw, th), Image.LANCZOS)

img = Image.new('RGB', (W, H), PAPER)
d = ImageDraw.Draw(img)

# ---------- masthead ----------
d.text((W // 2, 16), 'THE WORLD IN ONE PICTURE', font=font(SERIF_B, 44),
       fill=INK, anchor='ma')
d.text((W // 2, 68), 'TUESDAY, 24 NOVEMBER 2026', font=font(SANS_B, 36),
       fill=RED, anchor='ma')
d.line([(14, 114), (1010, 114)], fill=RULE, width=3)
d.line([(14, 120), (1010, 120)], fill=RULE, width=1)

# ---------- lead story: one dominant image + giant headline ----------
y = 132
nvidia = fit(f'{PANELS}/media-generation-panel-nvidia-0-ed6cf337-0eb8-4f52-ba21-dbeffca0a46a.png',
             1000, 500)
img.paste(nvidia, (12, y))
y += 500 + 12
f_h = font(SANS_B, 60)
lines = wrap(d, 'HUANG IS BACK AT NVIDIA', f_h, 1000)
assert len(lines) == 1, f'lead headline wrapped: {lines}'
d.text((12, y), lines[0], font=f_h, fill=INK)
y += 80
f_s = font(SANS, 28)
sub = 'Board reinstates Jensen Huang, 11 days after he resigned.'
assert d.textlength(sub, font=f_s) <= 1000, 'subline too wide'
d.text((12, y), sub, font=f_s, fill=INK)
y += 40
d.line([(14, y), (1010, y)], fill=RULE, width=2)
y += 16

# ---------- the other three stories: large text-only lines ----------
stories = [
    ('POLAND', 'Missiles land; NATO sends AWACS'),
    ('LIBYA', 'Ukraine sinks a Russian warship'),
    ('IRAN', 'Tehran defies the U.S. naval blockade'),
]
f_k = font(SANS_B, 36)
f_t = font(SANS_B, 36)
for kicker, text in stories:
    kx = 12
    d.text((kx, y), kicker + ' — ', font=f_k, fill=RED)
    kw = d.textlength(kicker + ' — ', font=f_k)
    d.text((kx + kw, y), text, font=f_t, fill=INK)
    y += 54
assert y <= 1012, f'layout overflow: end y = {y}'

img.save(OUT, 'JPEG', quality=90, optimize=True)
print('saved', OUT, os.path.getsize(OUT), 'bytes; end y =', y)
