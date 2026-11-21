#!/usr/bin/env python3
"""Render an open passport spread for the invented Republic of Ostravia.

Deterministic: no randomness, no network. Writes one image (1024x768)
to $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png). If the PNG
would exceed 1,048,576 bytes, JPEG bytes are written to the same path
(the gate accepts PNG or JPEG content).
"""

import datetime
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# The grader's bare python:3.13 image has no Pillow and no fonts, so both
# ship inside deps.zip next to this file and are extracted to the temp
# dir on first run (the grader gives the entry a writable /tmp).
import tempfile
import zipfile

_DEPS_DIR = os.path.join(tempfile.gettempdir(), "ostravia-deps")
if not os.path.isdir(os.path.join(_DEPS_DIR, "vendor", "PIL")):
    with zipfile.ZipFile(os.path.join(HERE, "deps.zip")) as _z:
        _z.extractall(_DEPS_DIR)
sys.path.insert(0, os.path.join(_DEPS_DIR, "vendor"))

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1024, 768
PAGE = W // 2  # each page is 512 wide

FONT_DIR = os.path.join(_DEPS_DIR, "fonts")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
MONO = os.path.join(FONT_DIR, "DejaVuSansMono.ttf")
MONO_B = os.path.join(FONT_DIR, "DejaVuSansMono-Bold.ttf")

_font_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


# ---------------------------------------------------------------- document data
COUNTRY_EN = "REPUBLIC OF OSTRAVIA"
COUNTRY_OS = "REPUBLIKA OSTRAVIJA"
CODE = "OVR"

HOLDER = {
    "surname": "MERAVIK",
    "given": "ILONA",
    "nationality": "OSTRAVIAN",
    "dob": datetime.date(1989, 3, 14),
    "sex": "F",
    "pob": "VELIGRAD",
    "docno": "OV4182073",
    "issue": datetime.date(2021, 6, 3),
    "expiry": datetime.date(2031, 6, 3),
    "authority": "MINISTRY OF THE INTERIOR \u2014 VELIGRAD",
}

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def fmt_date(d):
    return "%02d %s %04d" % (d.day, MONTHS[d.month - 1], d.year)


# Border stamps: (country, border post, kind, date, ink, shape)
INK_BLUE = (32, 62, 138)
INK_RED = (168, 42, 42)
INK_BLACK = (38, 38, 38)
D = datetime.date
STAMPS = [
    ("OSTRAVIA", "VELIGRAD RAIL", "EXIT",  D(2022, 10, 14), INK_BLUE, "rect"),
    ("KHARADIA", "MERAN BRIDGE",  "ENTRY", D(2022, 10, 14), INK_RED, "round"),
    ("KHARADIA", "MERAN BRIDGE",  "EXIT",  D(2022, 10, 21), INK_RED, "round"),
    ("OSTRAVIA", "VELIGRAD RAIL", "ENTRY", D(2022, 10, 21), INK_BLUE, "rect"),
    ("OSTRAVIA", "VESS JUNCTION", "EXIT",  D(2024, 5, 9),   INK_BLUE, "rect"),
    ("LUTHENIA", "VESS JUNCTION", "ENTRY", D(2024, 5, 9),   INK_BLACK, "oval"),
    ("LUTHENIA", "VESS JUNCTION", "EXIT",  D(2024, 5, 16),  INK_BLACK, "oval"),
    ("OSTRAVIA", "VESS JUNCTION", "ENTRY", D(2024, 5, 16),  INK_BLUE, "rect"),
    ("OSTRAVIA", "VELIGRAD RAIL", "EXIT",  D(2025, 9, 5),   INK_BLUE, "rect"),
    ("KHARADIA", "MERAN BRIDGE",  "ENTRY", D(2025, 9, 5),   INK_RED, "round"),
    ("KHARADIA", "MERAN BRIDGE",  "EXIT",  D(2025, 9, 12),  INK_RED, "round"),
    ("OSTRAVIA", "VELIGRAD RAIL", "ENTRY", D(2025, 9, 12),  INK_BLUE, "rect"),
]
for _c, _p, _k, _dt, _i, _s in STAMPS:
    assert HOLDER["issue"] < _dt <= D(2026, 11, 21), _dt

VISA_ISSUE = D(2022, 9, 28)
assert HOLDER["issue"] < VISA_ISSUE < STAMPS[0][3]

# ---------------------------------------------------------------- colours
PAPER = (246, 242, 230)
PAPER_DARK = (232, 226, 208)
NAVY = (24, 44, 88)
INK = (28, 28, 30)
LABEL = (92, 96, 106)
RULE = (120, 124, 130)
GUIL1 = (233, 235, 226)
GUIL2 = (229, 233, 241)
MICRO = (178, 182, 170)


# ---------------------------------------------------------------- helpers
def draw_spaced(dr, xy, text, font, fill, spacing=2):
    """Draw text with extra letter spacing; returns total width."""
    x, y = xy
    for ch in text:
        dr.text((x, y), ch, font=font, fill=fill)
        x += dr.textlength(ch, font=font) + spacing
    return x - spacing - xy[0]


def text_w(dr, text, font):
    return dr.textlength(text, font=font)


def spaced_w(dr, text, font, spacing=2):
    return sum(dr.textlength(c, font=font) for c in text) + spacing * (len(text) - 1)


# ---------------------------------------------------------------- background
def background():
    img = Image.new("RGB", (W, H), PAPER)
    dr = ImageDraw.Draw(img)
    # guilloche: two families of gentle sine lines
    for base in range(-10, H + 10, 13):
        pts = [(x, base + 3.0 * math.sin(x * 0.020 + base * 0.15))
               for x in range(0, W + 1, 8)]
        dr.line(pts, fill=GUIL1, width=1)
    for base in range(-10, H + 10, 26):
        pts = [(x, base + 5.0 * math.sin(x * 0.011 + base * 0.07 + 2.0))
               for x in range(0, W + 1, 8)]
        dr.line(pts, fill=GUIL2, width=1)
    # seam + outer-edge shading (book gutter)
    for i in range(46):
        t = i / 46.0
        shade = int(26 * (1 - t) ** 2)
        col = tuple(max(0, c - shade) for c in PAPER)
        dr.line([(PAGE - 46 + i, 0), (PAGE - 46 + i, H)], fill=col)
        dr.line([(PAGE + 46 - i, 0), (PAGE + 46 - i, H)], fill=col)
    for i in range(14):
        t = i / 14.0
        shade = int(16 * (1 - t) ** 2)
        col = tuple(max(0, c - shade) for c in PAPER)
        dr.line([(i, 0), (i, H)], fill=col)
        dr.line([(W - 1 - i, 0), (W - 1 - i, H)], fill=col)
        dr.line([(0, i), (W, i)], fill=col)
        dr.line([(0, H - 1 - i), (W, H - 1 - i)], fill=col)
    # page frames + microprint borders
    for x0 in (18, PAGE + 18):
        x1 = x0 + PAGE - 36
        dr.rectangle([x0, 18, x1, H - 18], outline=(196, 198, 188), width=1)
        micro = "REPUBLIKA OSTRAVIJA \u00b7 REPUBLIC OF OSTRAVIA \u00b7 "
        f = F(SANS, 7)
        unit = text_w(dr, micro, f)
        x = x0 + 4
        while x < x1 - 6:
            dr.text((x, 21), micro, font=f, fill=MICRO)
            x += unit
        x = x0 + 4
        while x < x1 - 6:
            dr.text((x, H - 30), micro, font=f, fill=MICRO)
            x += unit
    return img


# ---------------------------------------------------------------- crest
def crest(dr, cx, cy, s):
    """Simple geometric crest: shield, horizontal bars, five-point star."""
    w2, h2 = s * 0.62, s * 0.78
    shield = [(cx - w2, cy - h2), (cx + w2, cy - h2), (cx + w2, cy + h2 * 0.25),
              (cx, cy + h2), (cx - w2, cy + h2 * 0.25)]
    dr.polygon(shield, outline=NAVY, width=2)
    dr.line([(cx - w2, cy - h2 * 0.42), (cx + w2, cy - h2 * 0.42)], fill=NAVY, width=2)
    # star
    r1, r2 = s * 0.30, s * 0.125
    pts = []
    for i in range(10):
        r = r1 if i % 2 == 0 else r2
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + r * math.cos(a), cy + s * 0.18 + r * math.sin(a)))
    dr.polygon(pts, fill=NAVY)
    dr.line([(cx - w2, cy + h2 * 0.25), (cx + w2, cy + h2 * 0.25)], fill=NAVY, width=1)


# ---------------------------------------------------------------- portrait
def load_portrait():
    src = Image.open(os.path.join(HERE, "portrait.jpg")).convert("RGB")
    # crop to ID ratio 35:45, biased to the top (head and shoulders)
    tw = src.width
    th = int(tw * 45 / 35)
    top = max(0, (src.height - th) // 6)
    src = src.crop((0, top, tw, top + th))
    return src


# ---------------------------------------------------------------- MRZ
def icao_cd(s):
    weights = (7, 3, 1)
    total = 0
    for i, ch in enumerate(s):
        if ch.isdigit():
            v = int(ch)
        elif ch == "<":
            v = 0
        else:
            v = ord(ch) - 55  # A=10 .. Z=35
        total += v * weights[i % 3]
    return str(total % 10)


def mrz_lines():
    name = (HOLDER["surname"] + "<<" + HOLDER["given"]).ljust(44 - 5, "<")
    line1 = "P<" + CODE + name
    doc = HOLDER["docno"]
    dob = HOLDER["dob"].strftime("%y%m%d")
    exp = HOLDER["expiry"].strftime("%y%m%d")
    personal = "<" * 14
    body = (doc + icao_cd(doc) + CODE
            + dob + icao_cd(dob) + HOLDER["sex"]
            + exp + icao_cd(exp)
            + personal + icao_cd(personal))
    composite = icao_cd(body[0:10] + body[13:20] + body[21:43])
    line2 = body + composite
    assert len(line1) == 44 and len(line2) == 44, (line1, line2)
    return line1, line2


# ---------------------------------------------------------------- stamps
def make_stamp(country, post, kind, date, ink, shape):
    w, h, pad = 196, 76, 14
    layer = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    dr = ImageDraw.Draw(layer)
    box = [pad, pad, pad + w, pad + h]
    a = 205
    col = ink + (a,)
    if shape == "rect":
        dr.rectangle(box, outline=col, width=3)
        dr.rectangle([box[0] + 5, box[1] + 5, box[2] - 5, box[3] - 5],
                     outline=col, width=1)
    elif shape == "round":
        dr.rounded_rectangle(box, radius=14, outline=col, width=3)
        dr.rounded_rectangle([box[0] + 5, box[1] + 5, box[2] - 5, box[3] - 5],
                             radius=10, outline=col, width=1)
    else:  # oval
        dr.ellipse(box, outline=col, width=3)
        dr.ellipse([box[0] + 5, box[1] + 5, box[2] - 5, box[3] - 5],
                   outline=col, width=1)
    cx = pad + w / 2
    f1, f2, f3 = F(SANS_B, 14), F(SANS, 10), F(SANS_B, 13)
    dr.text((cx, pad + 8), country, font=f1, fill=col, anchor="ma")
    dr.text((cx, pad + 29), post, font=f2, fill=col, anchor="ma")
    dr.text((cx, pad + 47), "%s \u00b7 %s" % (fmt_date(date), kind),
            font=f3, fill=col, anchor="ma")
    return layer.filter(ImageFilter.GaussianBlur(0.4))


def paste_rot(base, layer, cx, cy, angle):
    rot = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    base.paste(rot, (int(cx - rot.width / 2), int(cy - rot.height / 2)), rot)


# ---------------------------------------------------------------- left page
def field(dr, x, y, label_os, label_en, value, vw=None, bold=True, vsize=13):
    dr.text((x, y), "%s / %s" % (label_os, label_en), font=F(SANS, 8), fill=LABEL)
    dr.text((x, y + 11), value, font=F(SANS_B if bold else SANS, vsize), fill=INK)


def left_page(img, portrait):
    dr = ImageDraw.Draw(img)
    # header
    crest(dr, 66, 66, 46)
    cx = 292
    f = F(SERIF_B, 21)
    dr.text((cx, 34), COUNTRY_EN, font=f, fill=NAVY, anchor="ma")
    f = F(SERIF, 14)
    dr.text((cx, 63), COUNTRY_OS, font=f, fill=(70, 76, 88), anchor="ma")
    f = F(SANS_B, 11)
    w = spaced_w(dr, "PASSPORT \u2014 PASO\u0160", f, 3)
    draw_spaced(dr, (cx - w / 2, 90), "PASSPORT \u2014 PASO\u0160", f, NAVY, 3)
    dr.line([(36, 116), (476, 116)], fill=NAVY, width=2)
    dr.line([(36, 120), (476, 120)], fill=RULE, width=1)

    # portrait with thin border + ghost copy
    ph = portrait.resize((150, 193), Image.LANCZOS)
    img.paste(ph, (36, 148))
    dr.rectangle([36, 148, 186, 341], outline=(60, 60, 60), width=1)
    ghost = portrait.resize((72, 93), Image.LANCZOS)
    ghost = Image.blend(ghost, Image.new("RGB", ghost.size, PAPER), 0.62)
    img.paste(ghost, (392, 452))
    dr.text((428, 548), "OSTRAVIJA \u00b7 OVR", font=F(SANS, 7),
            fill=(150, 152, 142), anchor="ma")

    # data fields, right of the portrait
    fx = 204
    field(dr, fx, 148, "TIP", "TYPE", "P")
    field(dr, 330, 148, "KODA", "CODE", CODE)
    field(dr, fx, 190, "PASO\u0160 \u0160T.", "PASSPORT NO", HOLDER["docno"], vsize=14)
    field(dr, fx, 234, "PRIIMEK", "SURNAME", HOLDER["surname"], vsize=14)
    field(dr, fx, 278, "IME", "GIVEN NAMES", HOLDER["given"], vsize=14)
    field(dr, fx, 322, "DR\u017dAVLJANSTVO", "NATIONALITY", HOLDER["nationality"])
    field(dr, 36, 356, "DATUM ROJSTVA", "DATE OF BIRTH", fmt_date(HOLDER["dob"]))
    field(dr, 204, 356, "SPOL", "SEX", HOLDER["sex"])
    field(dr, 268, 356, "KRAJ ROJSTVA", "PLACE OF BIRTH", HOLDER["pob"])
    field(dr, 36, 400, "DATUM IZDAJE", "DATE OF ISSUE", fmt_date(HOLDER["issue"]))
    field(dr, 268, 400, "VELJA DO", "DATE OF EXPIRY", fmt_date(HOLDER["expiry"]))

    # authority, full width
    field(dr, 36, 452, "IZDAL", "AUTHORITY", HOLDER["authority"], vsize=12)

    # signature
    dr.text((36, 502), "PODPIS IMETNIKA / SIGNATURE OF HOLDER",
            font=F(SANS, 8), fill=LABEL)
    pts = []
    for i in range(161):
        t = i / 160.0
        x = 44 + t * 230
        y = (542 - 20 * math.exp(-((t - 0.13) ** 2) / 0.002)   # tall first stroke
             + 9 * math.exp(-((t - 0.24) ** 2) / 0.001)        # dip back down
             - 11 * math.exp(-((t - 0.38) ** 2) / 0.003)       # second name hump
             - 5 * math.sin(t * 34.0) * math.exp(-t * 1.6)     # small letter teeth
             + 6 * math.exp(-((t - 0.78) ** 2) / 0.002)        # final rise
             - 13 * t * t * (1 - t))                           # trailing fall
        pts.append((x, y))
    dr.line(pts, fill=(22, 32, 92), width=2)
    dr.line([(44, 556), (292, 556)], fill=(22, 32, 92), width=1)  # flourish
    dr.line([(36, 566), (330, 566)], fill=RULE, width=1)

    # MRZ
    line1, line2 = mrz_lines()
    dr.line([(36, 622), (476, 622)], fill=RULE, width=1)
    f = F(MONO_B, 16)
    dr.text((36, 640), line1, font=f, fill=(40, 40, 40))
    dr.text((36, 668), line2, font=f, fill=(40, 40, 40))


# ---------------------------------------------------------------- right page
def right_page(img):
    dr = ImageDraw.Draw(img)
    x0 = PAGE + 36
    cx = PAGE + PAGE // 2
    f = F(SERIF_B, 17)
    dr.text((cx, 36), "VISAS \u2014 VIZE", font=f, fill=NAVY, anchor="ma")
    dr.text((988, 34), "4", font=F(SANS_B, 13), fill=NAVY, anchor="ra")
    dr.line([(x0, 72), (988, 72)], fill=NAVY, width=2)
    dr.line([(x0, 76), (988, 76)], fill=RULE, width=1)
    dr.text((cx, 84), "Border stamps and visas \u00b7 Mejni \u017eigi in vize",
            font=F(SANS, 9), fill=LABEL, anchor="ma")

    # --- Kharadian visa sticker (the telling detail) ---
    sx, sy, sw, sh = PAGE + 44, 108, 316, 118
    sticker = Image.new("RGB", (sw, sh), (238, 240, 226))
    sd = ImageDraw.Draw(sticker)
    sd.rectangle([0, 0, sw - 1, sh - 1], outline=(120, 128, 110), width=2)
    sd.rectangle([4, 4, sw - 5, sh - 5], outline=(170, 176, 158), width=1)
    sd.text((14, 10), "KHARADIA", font=F(SERIF_B, 15), fill=(96, 30, 30))
    sd.text((sw - 14, 8), "VISA", font=F(SERIF_B, 17), fill=(96, 30, 30), anchor="ra")
    sd.line([(12, 36), (sw - 12, 36)], fill=(150, 90, 90), width=1)
    sd.text((14, 44), "SINGLE ENTRY \u00b7 30 DAYS", font=F(SANS_B, 11), fill=INK)
    sd.text((14, 62), "VALID FOR ENTRY BY ROAD OR RAIL ONLY",
            font=F(SANS_B, 10), fill=(150, 32, 32))
    sd.text((14, 82), "No K-2022-04817 \u00b7 Issued at VELIGRAD, %s" % fmt_date(VISA_ISSUE),
            font=F(SANS, 9), fill=(70, 70, 70))
    sd.text((14, 97), "MERAVIK ILONA \u00b7 Passport %s" % HOLDER["docno"],
            font=F(SANS, 9), fill=(70, 70, 70))
    img.paste(sticker, (sx, sy))
    dr = ImageDraw.Draw(img)

    # round fee stamp overlapping the sticker's lower-right corner
    fee = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fee)
    col = (104, 52, 128, 215)
    fd.ellipse([6, 6, 114, 114], outline=col, width=3)
    fd.ellipse([12, 12, 108, 108], outline=col, width=1)
    fd.text((60, 34), "FEE PAID", font=F(SANS_B, 13), fill=col, anchor="ma")
    fd.text((60, 54), "40 OK", font=F(SANS_B, 15), fill=col, anchor="ma")
    fd.text((60, 78), fmt_date(VISA_ISSUE), font=F(SANS, 8), fill=col, anchor="ma")
    fee = fee.filter(ImageFilter.GaussianBlur(0.4))
    paste_rot(img, fee, sx + sw - 6, sy + sh + 2, -11)

    # --- border stamps, chronological, two loose columns ---
    angles = [-4.5, 2, -1.5, 5, -6, 1.5, -3.5, 3, -1, 5.5, -2.5, 1]
    jx = [0, 7, -6, 4, -8, 5, 1, -4, 7, -6, 3, -3]
    jy = [0, -3, 4, 0, -4, 3, 5, -2, 0, 4, -3, 2]
    for i, (country, post, kind, date, ink, shape) in enumerate(STAMPS):
        col_i = i % 2
        row_i = i // 2
        cx_s = PAGE + 150 + col_i * 224 + jx[i]
        cy_s = 292 + row_i * 80 + jy[i]
        layer = make_stamp(country, post, kind, date, ink, shape)
        paste_rot(img, layer, cx_s, cy_s, angles[i])


# ---------------------------------------------------------------- main
def render():
    img = background()
    portrait = load_portrait()
    left_page(img, portrait)
    right_page(img)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    img = render()
    img.save(path, format="PNG", optimize=True)
    if os.path.getsize(path) > 1_048_576:
        img.save(path, format="JPEG", quality=88)
    print("wrote", path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
