#!/usr/bin/env python3
"""Build entry.png for the news-image-20261124 entry.

The four story illustrations live in ../news-image/panels (drawn in-session for
this day's news). This script composes them into one 1024x1024 newspaper front
page with crisp PIL text: masthead and date, the four picture stories, and an
"ALSO TODAY" strip for the rest of the day. Output is JPEG bytes in a file
named entry.png (the bounty rules allow PNG or JPEG bytes under that name),
1024x1024 and under 1 MiB.
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
d.text((W // 2, 66), 'TUESDAY, 24 NOVEMBER 2026', font=font(SANS_B, 28),
       fill=RED, anchor='ma')
d.line([(14, 106), (1010, 106)], fill=RULE, width=3)
d.line([(14, 112), (1010, 112)], fill=RULE, width=1)

LX0, LX1 = 12, 612      # left column
RX0, RX1 = 624, 1012    # right column
RW = RX1 - RX0

# ---------- left column: Nvidia ----------
y = 124
nvidia = fit(f'{PANELS}/media-generation-panel-nvidia-0-ed6cf337-0eb8-4f52-ba21-dbeffca0a46a.png',
             LX1 - LX0, 360)
img.paste(nvidia, (LX0, y))
y += 360 + 10
d.text((LX0, y), 'TECHNOLOGY', font=font(SANS_B, 20), fill=RED)
y += 28
f_h = font(SANS_B, 44)
y = draw_lines(d, wrap(d, 'HUANG IS BACK AT NVIDIA', f_h, LX1 - LX0),
               f_h, LX0, y, INK, 50)
y += 6
f_s = font(SANS, 21)
y = draw_lines(d, wrap(d, 'Board reinstates Jensen Huang as chief executive, '
                         '11 days after he resigned.', f_s, LX1 - LX0),
               f_s, LX0, y, INK, 27)
left_end = y

# ---------- right column: Poland, then Libya ----------
def story(path, kicker, headline, y0):
    im = fit(path, RW, 160)
    img.paste(im, (RX0, y0))
    y = y0 + 160 + 8
    d.text((RX0, y), kicker, font=font(SANS_B, 18), fill=RED)
    y += 24
    f = font(SANS_B, 24)
    y = draw_lines(d, wrap(d, headline, f, RW), f, RX0, y, INK, 29)
    return y

y = 124
y = story(f'{PANELS}/media-generation-panel-poland-0-5ccc060a-78de-48d5-82e4-7ad16b562b6a.png',
          'EUROPE', 'MISSILES LAND IN POLAND — NATO SENDS AWACS', y)
y += 12
y = story(f'{PANELS}/media-generation-panel-libya-0-d13a0659-0a49-4d80-94e2-efecdfe7648a.png',
          'THE WAR SPREADS', 'UKRAINE SINKS RUSSIAN WARSHIP IN LIBYA', y)
right_end = y

# ---------- row 2: Iran banner with overlaid headline ----------
row2 = max(left_end, right_end) + 12
assert row2 + 190 + 12 + 116 <= 1012, f'layout overflow: row2={row2}'
iran = fit(f'{PANELS}/media-generation-panel-iran-0-b7eba82d-f5f8-4cb6-a4e3-04f96fcf8e68.png',
           1000, 190)
img.paste(iran, (12, row2))
overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
od = ImageDraw.Draw(overlay)
od.rectangle([12, row2 + 190 - 46, 1012, row2 + 190], fill=(0, 0, 0, 175))
img.paste(Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB'), (0, 0))
d = ImageDraw.Draw(img)
d.text((24, row2 + 190 - 40),
       "IRAN DEFIES U.S. NAVAL BLOCKADE — Tehran vows to use 'all its tools'",
       font=font(SANS_B, 23), fill=(255, 255, 255))

# ---------- ALSO TODAY strip ----------
y = row2 + 190 + 12
d.text((12, y), 'ALSO TODAY', font=font(SANS_B, 18), fill=RED)
y += 24
f_it = font(SANS, 18)
items_l = [
    'CLIMATE TALKS COLLAPSE — UN talks in Turkey fail',
    "MEXICO NABS 'EL CHAPO ISIDRO' — with U.S. help",
    'RUSSIAN JETS ENTER S. KOREA AIRSPACE',
]
items_r = [
    'VANUATU HIT BY 6.5 QUAKE — no tsunami threat',
    'GAZA STRIKES KILL THREE — incl. a UN aid worker',
    "SK HYNIX +20% — on Huang's Nvidia return",
]
for a, b in zip(items_l, items_r):
    d.text((12, y), a, font=f_it, fill=INK)
    d.text((518, y), b, font=f_it, fill=INK)
    y += 26
assert y <= 1012, f'strip overflow: y={y}'

img.save(OUT, 'JPEG', quality=90, optimize=True)
print('saved', OUT, os.path.getsize(OUT), 'bytes; row2 =', row2, 'end y =', y)
