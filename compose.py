#!/usr/bin/env python3
"""Build entry.png for the news-image-20261124 entry (v3).

The four story illustrations live in ../news-image/panels (drawn in-session for
this day's news). This script composes them into one 1024x1024 newspaper front
page with crisp PIL text: masthead and date, and the four picture stories.

v3 (after round 1 judged v2 at rank 6,887 of 7,302, 28.94%): at the ~300 px
width the judge reads at, v2's right-column headlines (26 px) and the Iran
banner headline (24 px) were barely readable, and every subline/kicker was
unreadable — so the judge could clearly read only the Nvidia headline. v3
fixes that directly: every headline is at least 40 px (about 12 px at 300 px
reading width), there are no sublines at all (the headlines carry the stories),
and the Iran headline sits in a large white-on-dark band instead of a 24 px
overlay line. Output is JPEG bytes in a file named entry.png (the bounty rules
allow PNG or JPEG bytes under that name), 1024x1024 and under 1 MiB.
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

def draw_lines(draw, lines, fnt, x, y, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y

def fit(path, tw, th):
    im = Image.open(path).convert('RGB')
    return ImageOps.fit(im, (tw, th), Image.LANCZOS)

img = Image.new('RGB', (W, H), PAPER)
d = ImageDraw.Draw(img)

# ---------- masthead ----------
d.text((W // 2, 16), 'THE WORLD IN ONE PICTURE', font=font(SERIF_B, 44),
       fill=INK, anchor='ma')
d.text((W // 2, 68), 'TUESDAY, 24 NOVEMBER 2026', font=font(SANS_B, 32),
       fill=RED, anchor='ma')
d.line([(14, 110), (1010, 110)], fill=RULE, width=3)
d.line([(14, 116), (1010, 116)], fill=RULE, width=1)

# ---------- main story: Nvidia, full width ----------
y = 128
nvidia = fit(f'{PANELS}/media-generation-panel-nvidia-0-ed6cf337-0eb8-4f52-ba21-dbeffca0a46a.png',
             1000, 260)
img.paste(nvidia, (12, y))
y += 280 + 10
d.text((12, y), 'TECHNOLOGY', font=font(SANS_B, 24), fill=RED)
y += 32
f_h = font(SANS_B, 64)
lines = wrap(d, 'HUANG IS BACK AT NVIDIA', f_h, 1000)
assert len(lines) == 1, f'Nvidia headline wrapped: {lines}'
y = draw_lines(d, lines, f_h, 12, y, INK, 72)
main_end = y

# ---------- second row: Poland (left) and Libya (right) ----------
COL_W = 494
LX0, RX0 = 12, 518

def story(path, kicker, headline, x0, y0):
    im = fit(path, COL_W, 170)
    img.paste(im, (x0, y0))
    y = y0 + 170 + 8
    d.text((x0, y), kicker, font=font(SANS_B, 22), fill=RED)
    y += 28
    f = font(SANS_B, 40)
    lines = wrap(d, headline, f, COL_W)
    assert len(lines) <= 3, f'headline too long: {lines}'
    y = draw_lines(d, lines, f, x0, y, INK, 47)
    return y

y = main_end + 12
y_left = story(f'{PANELS}/media-generation-panel-poland-0-5ccc060a-78de-48d5-82e4-7ad16b562b6a.png',
               'EUROPE', 'MISSILES LAND IN POLAND — NATO SENDS AWACS', LX0, y)
y_right = story(f'{PANELS}/media-generation-panel-libya-0-d13a0659-0a49-4d80-94e2-efecdfe7648a.png',
                'THE WAR SPREADS', 'UKRAINE SINKS RUSSIAN WARSHIP IN LIBYA', RX0, y)
row_end = max(y_left, y_right)

# ---------- row 3: Iran banner, large white headline on a dark band ----------
row3 = row_end + 10
iran_h = 1012 - row3
assert iran_h >= 110, f'Iran banner too short: {iran_h}'
iran = fit(f'{PANELS}/media-generation-panel-iran-0-b7eba82d-f5f8-4cb6-a4e3-04f96fcf8e68.png',
           1000, iran_h)
img.paste(iran, (12, row3))
overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
od = ImageDraw.Draw(overlay)
od.rectangle([12, row3 + iran_h - 56, 1012, row3 + iran_h], fill=(0, 0, 0, 178))
img.paste(Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB'), (0, 0))
d = ImageDraw.Draw(img)
f_i = font(SANS_B, 40)
iran_lines = wrap(d, "IRAN DEFIES U.S. NAVAL BLOCKADE", f_i, 960)
assert len(iran_lines) == 1, f'Iran headline wrapped: {iran_lines}'
d.text((24, row3 + iran_h - 50), iran_lines[0], font=f_i, fill=(255, 255, 255))

img.save(OUT, 'JPEG', quality=90, optimize=True)
print('saved', OUT, os.path.getsize(OUT), 'bytes; main_end =', main_end,
      'row_end =', row_end, 'row3 =', row3, 'iran_h =', iran_h)
