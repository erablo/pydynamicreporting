"""
Render a NEBS packaging drop-test sequence as a clean titled box (PNG).

Data taken from the source table:
  Flat drops  : S1..S6            (drops 1-6)
  Edge drops  : E2-3, E2-5, E5-3  (drops 7-9)
  Corner drops: C1-2-6, C1-4-5,
                C2-3-5, C3-4-5    (drops 10-13)
"""

from PIL import Image, ImageDraw, ImageFont
import sys

# ---------------------------------------------------------------- palette
ERICSSON_BLUE = (0x00, 0x30, 0x56)
ACCENT = (0x00, 0x82, 0xF0)
TEAL = (0x00, 0xA9, 0xA5)
PURPLE = (0x62, 0x2D, 0x6E)
GRAY = (0x53, 0x53, 0x5A)
LIGHT = (0xF2, 0xF2, 0xF4)
WHITE = (0xFF, 0xFF, 0xFF)
ROW_ALT = (0xE9, 0xEE, 0xF4)

# ---------------------------------------------------------------- data
rows = [
    (1, "Flat drop S1", "flat"), (2, "Flat drop S2", "flat"),
    (3, "Flat drop S3", "flat"), (4, "Flat drop S4", "flat"),
    (5, "Flat drop S5", "flat"), (6, "Flat drop S6", "flat"),
    (7, "Edge drop E2-3", "edge"), (8, "Edge drop E2-5", "edge"),
    (9, "Edge drop E5-3", "edge"),
    (10, "Corner drop C1-2-6", "corner"), (11, "Corner drop C1-4-5", "corner"),
    (12, "Corner drop C2-3-5", "corner"), (13, "Corner drop C3-4-5", "corner"),
]

TYPE_COLOR = {"flat": TEAL, "edge": ACCENT, "corner": PURPLE}

# ---------------------------------------------------------------- fonts
def load_font(size, bold=False):
    names = (["arialbd.ttf", "Arialbd.ttf"] if bold else ["arial.ttf", "Arial.ttf"])
    for n in names:
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            continue
    try:
        return ImageFont.truetype(
            "C:/Windows/Fonts/" + ("arialbd.ttf" if bold else "arial.ttf"), size)
    except OSError:
        return ImageFont.load_default()

f_title = load_font(40, bold=True)
f_sub = load_font(22)
f_hdr = load_font(22, bold=True)
f_cell = load_font(22)
f_num = load_font(22, bold=True)
f_legend = load_font(19)
f_foot = load_font(16)

# ---------------------------------------------------------------- layout
W = 1240
margin = 50
box_x0, box_y0 = margin, margin
box_x1 = W - margin

title_h = 110
col_no_w = 110          # drop-no column width
pad = 28
header_row_h = 50
row_h = 46
legend_h = 70
foot_h = 44

# two logical columns (split the 13 rows: 7 left / 6 right like the source)
left = rows[:7]
right = rows[7:]
n_body_rows = max(len(left), len(right))

inner_w = (box_x1 - box_x0) - 2 * pad
half_w = inner_w // 2
gap = 40

table_top = box_y0 + title_h + pad
table_h = header_row_h + n_body_rows * row_h
box_y1 = table_top + table_h + pad + legend_h + foot_h

H = box_y1 + margin

img = Image.new("RGB", (W, H), WHITE)
d = ImageDraw.Draw(img)


def rounded(xy, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def text_center(cx, cy, s, font, fill):
    bb = d.textbbox((0, 0), s, font=font)
    w = bb[2] - bb[0]; h = bb[3] - bb[1]
    d.text((cx - w / 2, cy - h / 2 - bb[1]), s, font=font, fill=fill)


def text_mid_left(x, cy, s, font, fill):
    bb = d.textbbox((0, 0), s, font=font)
    h = bb[3] - bb[1]
    d.text((x, cy - h / 2 - bb[1]), s, font=font, fill=fill)


# ---- outer box
rounded([box_x0, box_y0, box_x1, box_y1], 18, fill=WHITE, outline=ERICSSON_BLUE, width=3)

# ---- title band
d.rounded_rectangle([box_x0, box_y0, box_x1, box_y0 + title_h], radius=18,
                    fill=ERICSSON_BLUE)
d.rectangle([box_x0, box_y0 + title_h - 20, box_x1, box_y0 + title_h], fill=ERICSSON_BLUE)
d.rectangle([box_x0, box_y0 + title_h - 6, box_x1, box_y0 + title_h], fill=ACCENT)
text_mid_left(box_x0 + pad, box_y0 + 38, "NEBS Packaging Drop-Test Sequence",
              f_title, WHITE)
text_mid_left(box_x0 + pad, box_y0 + 82,
              "13 drops  \u2013  6 flat  \u00b7  3 edge  \u00b7  4 corner   (GR-63-CORE)",
              f_sub, (0xBF, 0xD9, 0xF2))


def draw_half(x0, data):
    """Draw one logical half-table starting at x0."""
    no_x0 = x0
    no_x1 = x0 + col_no_w
    det_x0 = no_x1
    det_x1 = x0 + half_w
    # header
    d.rectangle([no_x0, table_top, det_x1, table_top + header_row_h], fill=ERICSSON_BLUE)
    text_center((no_x0 + no_x1) / 2, table_top + header_row_h / 2, "Drop no.", f_hdr, WHITE)
    text_mid_left(det_x0 + 18, table_top + header_row_h / 2, "Drop details", f_hdr, WHITE)
    # body
    for i, (no, det, typ) in enumerate(data):
        ry0 = table_top + header_row_h + i * row_h
        ry1 = ry0 + row_h
        d.rectangle([no_x0, ry0, det_x1, ry1], fill=(ROW_ALT if i % 2 else WHITE))
        # type color chip on the left edge of the detail cell
        chip = TYPE_COLOR[typ]
        d.rectangle([det_x0 + 6, ry0 + 10, det_x0 + 14, ry1 - 10], fill=chip)
        cy = (ry0 + ry1) / 2
        text_center((no_x0 + no_x1) / 2, cy, str(no), f_num, ERICSSON_BLUE)
        text_mid_left(det_x0 + 26, cy, det, f_cell, GRAY)
    # grid lines
    d.rectangle([no_x0, table_top, det_x1,
                 table_top + header_row_h + len(data) * row_h],
                outline=(0xD5, 0xDA, 0xE0), width=1)
    d.line([no_x1, table_top, no_x1,
            table_top + header_row_h + len(data) * row_h],
           fill=(0xD5, 0xDA, 0xE0), width=1)


draw_half(box_x0 + pad, left)
draw_half(box_x0 + pad + half_w + gap, right)

# ---- legend
legend_y = table_top + table_h + pad + 10
lx = box_x0 + pad
items = [("Flat drops (faces S1\u2013S6)", TEAL),
         ("Edge drops (E)", ACCENT),
         ("Corner drops (C)", PURPLE)]
for label, col in items:
    d.rectangle([lx, legend_y, lx + 26, legend_y + 26], fill=col)
    text_mid_left(lx + 38, legend_y + 13, label, f_legend, GRAY)
    bb = d.textbbox((0, 0), label, font=f_legend)
    lx += 38 + (bb[2] - bb[0]) + 55

# ---- footer
d.line([box_x0 + pad, box_y1 - foot_h, box_x1 - pad, box_y1 - foot_h],
       fill=(0xD5, 0xDA, 0xE0), width=1)
text_mid_left(box_x0 + pad, box_y1 - foot_h / 2 + 2,
              "Edge/corner notation refers to the intersecting faces (e.g. E2-3 = edge "
              "between faces 2 and 3; C1-2-6 = corner at faces 1, 2 & 6).",
              f_foot, GRAY)
text_mid_left(box_x1 - pad - 90, box_y1 - foot_h / 2 + 2, "ERICSSON", f_foot, ERICSSON_BLUE)

out = sys.argv[1] if len(sys.argv) > 1 else "NEBS_Drop_Test_Sequence.png"
img.save(out, "PNG")
print("Saved:", out, img.size)
