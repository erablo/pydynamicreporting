"""
Render a corrugated box (isometric) with NEBS drop points annotated by arrows.

Face convention (per user reference drawing):
  1 = Top, 2 = Front, 3 = Bottom, 4 = Back, 5 = Left, 6 = Right
Box is a flat / wide carton (large top & front, short height).

Drops:
  - 6 flat / face drops  (S1..S6  -> faces 1..6)
  - 3 edge drops         (E2-3, E2-5, E5-3)
  - 4 corner drops       (C1-2-6, C1-4-5, C2-3-5, C3-4-5)

The corrugated look is drawn procedurally (kraft colors + flute texture),
so no external image / licensing is required.
"""

from PIL import Image, ImageDraw, ImageFont
import sys, math

# ------------------------------------------------------------ palette
ERICSSON_BLUE = (0x00, 0x30, 0x56)
ACCENT = (0x00, 0x82, 0xF0)
TEAL = (0x00, 0xA9, 0xA5)
PURPLE = (0x7A, 0x2B, 0x8E)
GRAY = (0x53, 0x53, 0x5A)
WHITE = (0xFF, 0xFF, 0xFF)

KRAFT_TOP = (0xD9, 0xA9, 0x6B)
KRAFT_FRONT = (0xC4, 0x8E, 0x50)
KRAFT_SIDE = (0xA9, 0x74, 0x3B)
KRAFT_EDGE = (0x6E, 0x49, 0x1F)

# ---- drop-status colors ----------------------------------------------------
SIM_GREEN = (0x1E, 0xA3, 0x4E)      # drops USED for drop-test simulation
NONSIM_GRAY = (0x8A, 0x92, 0x9B)    # physical test only (not simulated)

# the simulation subset requested
SIM_SET = {"S2", "S3", "S4", "E2-3", "E2-5", "C1-2-6"}


def status_color(name):
    return SIM_GREEN if name in SIM_SET else NONSIM_GRAY

W, H = 1500, 1020
img = Image.new("RGB", (W, H), WHITE)
d = ImageDraw.Draw(img, "RGBA")


# ------------------------------------------------------------ fonts
def font(sz, bold=False):
    try:
        return ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", sz)
    except OSError:
        try:
            return ImageFont.truetype(
                "C:/Windows/Fonts/" + ("arialbd.ttf" if bold else "arial.ttf"), sz)
        except OSError:
            return ImageFont.load_default()

f_title = font(42, bold=True)
f_sub = font(22)
f_face = font(28, bold=True)
f_lbl = font(20, bold=True)
f_leg = font(20)
f_foot = font(16)


def t_center(cx, cy, s, fnt, fill):
    bb = d.textbbox((0, 0), s, font=fnt)
    d.text((cx - (bb[2] - bb[0]) / 2, cy - (bb[3] - bb[1]) / 2 - bb[1]), s, font=fnt, fill=fill)


def t_left(x, cy, s, fnt, fill):
    bb = d.textbbox((0, 0), s, font=fnt)
    d.text((x, cy - (bb[3] - bb[1]) / 2 - bb[1]), s, font=fnt, fill=fill)


# ------------------------------------------------------------ title band
d.rectangle([0, 0, W, 110], fill=ERICSSON_BLUE)
d.rectangle([0, 104, W, 110], fill=ACCENT)
t_left(50, 40, "NEBS Drop Test \u2013 Simulation Scope", f_title, WHITE)
t_left(52, 86, "Green = simulated drop sequence  Drop 1\u20136  (S2, S3, S4, E2-3, E2-5, "
       "C1-2-6)  \u00b7  Gray = physical test only", f_sub, (0xBF, 0xD9, 0xF2))

# ============================================================ ISOMETRIC BOX
# Flat / wide carton.  Build 8 vertices.
#   T* = top plane, B* = bottom plane
#   FL front-left, FR front-right, BL back-left, BR back-right
fx, fy = 470, 560          # front-left-top anchor
bw = 430                   # width  (front face, left->right)
bh = 170                   # height (short, flat box)
dx, dy = 250, -160         # depth vector (towards back, up-right)

TFL = (fx, fy)
TFR = (fx + bw, fy)
TBL = (fx + dx, fy + dy)
TBR = (fx + bw + dx, fy + dy)

BFL = (fx, fy + bh)
BFR = (fx + bw, fy + bh)
BBL = (fx + dx, fy + bh + dy)
BBR = (fx + bw + dx, fy + bh + dy)

# ---- faces (painter's order: back/hidden first)
# Top face (1):  TFL TFR TBR TBL
d.polygon([TFL, TFR, TBR, TBL], fill=KRAFT_TOP, outline=KRAFT_EDGE)
# Right face (6): TFR TBR BBR BFR
d.polygon([TFR, TBR, BBR, BFR], fill=KRAFT_SIDE, outline=KRAFT_EDGE)
# Front face (2): TFL TFR BFR BFL
d.polygon([TFL, TFR, BFR, BFL], fill=KRAFT_FRONT, outline=KRAFT_EDGE)


# ---- corrugated flute texture on the exposed front thickness (bottom lip)
def flutes(p0, p1, vec, n, color=(0x8a, 0x5e, 0x2d, 170)):
    for i in range(n + 1):
        t = i / n
        x = p0[0] + (p1[0] - p0[0]) * t
        y = p0[1] + (p1[1] - p0[1]) * t
        d.line([(x, y), (x + vec[0], y + vec[1])], fill=color, width=1)

# thin flute strip along the top-front edge
flutes(TFL, TFR, (dx * 0.045, dy * 0.045), 50)

# ---- top seam / tape
d.line([((TFL[0] + TFR[0]) / 2, (TFL[1] + TFR[1]) / 2),
        ((TBL[0] + TBR[0]) / 2, (TBL[1] + TBR[1]) / 2)],
       fill=(0xE8, 0xD5, 0xB0, 220), width=9)

# ---- crisp visible edges
for a, b in [(TFL, TFR), (TFR, TBR), (TBR, TBL), (TBL, TFL),     # top
             (TFL, BFL), (TFR, BFR), (TBR, BBR),                 # verticals
             (BFL, BFR), (BFR, BBR)]:                            # bottom visible
    d.line([a, b], fill=KRAFT_EDGE, width=3)


# ---- face number badges on visible faces
def badge(center, label, color=ERICSSON_BLUE, r=24):
    x, y = center
    d.ellipse([x - r, y - r, x + r, y + r], fill=color, outline=WHITE, width=3)
    t_center(x, y, label, f_face, WHITE)

top_c = ((TFL[0] + TBR[0]) / 2, (TFL[1] + TBR[1]) / 2)
front_c = ((TFL[0] + BFR[0]) / 2, (TFL[1] + BFR[1]) / 2)
right_c = ((TFR[0] + BBR[0]) / 2, (TFR[1] + BBR[1]) / 2)
badge(top_c, "1")
badge(front_c, "2")
badge(right_c, "6")


# ---- hidden-face badges (3 Bottom, 4 Back, 5 Left) placed just outside the box
def hidden_badge(center, label, leader_to, r=22):
    """Outlined (hollow) badge for a hidden face, with a short dotted leader."""
    x, y = center
    # dotted leader
    lx0, ly0 = center
    lx1, ly1 = leader_to
    seglen = math.hypot(lx1 - lx0, ly1 - ly0)
    if seglen:
        ux, uy = (lx1 - lx0) / seglen, (ly1 - ly0) / seglen
        pos = r + 4
        while pos < seglen:
            a = (lx0 + ux * pos, ly0 + uy * pos)
            b = (lx0 + ux * min(pos + 7, seglen), ly0 + uy * min(pos + 7, seglen))
            d.line([a, b], fill=ERICSSON_BLUE, width=2)
            pos += 13
    d.ellipse([x - r, y - r, x + r, y + r], fill=WHITE, outline=ERICSSON_BLUE, width=3)
    t_center(x, y, label, f_face, ERICSSON_BLUE)


# Hidden faces are the opposites of the visible ones:
#   3 Bottom = opposite 1 Top ; 4 Back = opposite 2 Front ; 5 Left = opposite 6 Right
# To avoid the leader appearing to point at a *visible* face, each leader targets an
# edge that belongs uniquely to the hidden face (not shared with a visible face):
#   3 Bottom -> bottom-front edge (BFL-BFR), on the underside
#   4 Back   -> back-right vertical edge (TBR-BBR): clearly on the rear
#   5 Left   -> back-left vertical edge (TBL-BBL): the left face's rear edge
# Point each hidden-face leader at that face's OWN visible boundary edge, so it can
# never be mistaken for a neighbouring face:
#   3 Bottom -> bottom-front edge (BFL-BFR)  : the box's lower boundary (underside)
#   4 Back   -> back-top edge   (TBL-TBR)    : the top rear boundary of the box
#   5 Left   -> front-left vertical (TFL-BFL): the left boundary of the box (left face)
bottom_tgt = ((BFL[0] + BFR[0]) / 2, (BFL[1] + BFR[1]) / 2 + 14)
back_tgt = ((TBL[0] + TBR[0]) / 2, (TBL[1] + TBR[1]) / 2)
# aim 5 at the lower part of the front-left vertical edge (near BFL) to stay clear of
# the E2-5 arrow that approaches the upper part of that edge.
left_tgt = (BFL[0] - 4, BFL[1] - 45)

hidden_badge((bottom_tgt[0] - 30, bottom_tgt[1] + 150), "3", bottom_tgt)   # below  (opp. 1)
hidden_badge((back_tgt[0] - 70, back_tgt[1] - 210), "4", back_tgt)         # above rear edge, left of C1-4-5 (opp. 2)
hidden_badge((left_tgt[0] - 290, left_tgt[1] - 110), "5", left_tgt)        # left, points right to edge (opp. 6)

# faint "opposite-pair" tie-lines between the visible face badge and its hidden twin
def pair_line(a, b):
    seglen = math.hypot(b[0] - a[0], b[1] - a[1])
    if not seglen:
        return
    ux, uy = (b[0] - a[0]) / seglen, (b[1] - a[1]) / seglen
    pos = 26
    while pos < seglen - 26:
        p0 = (a[0] + ux * pos, a[1] + uy * pos)
        p1 = (a[0] + ux * min(pos + 4, seglen - 26), a[1] + uy * min(pos + 4, seglen - 26))
        d.line([p0, p1], fill=(0x9a, 0xa3, 0xad, 150), width=1)
        pos += 16


# ------------------------------------------------------------ drawing helpers
def arrow(start, end, color, width=4, head=16):
    d.line([start, end], fill=color, width=width)
    ang = math.atan2(end[1] - start[1], end[0] - start[0])
    for off in (math.radians(26), math.radians(-26)):
        hx = end[0] - head * math.cos(ang - off)
        hy = end[1] - head * math.sin(ang - off)
        d.line([end, (hx, hy)], fill=color, width=width)


def pill(x, y, text, color):
    bb = d.textbbox((0, 0), text, font=f_lbl)
    tw = bb[2] - bb[0]
    pad = 12
    d.rounded_rectangle([x, y, x + tw + 2 * pad, y + 40], radius=20, fill=color)
    t_left(x + pad, y + 20, text, f_lbl, WHITE)
    return (x, y, x + tw + 2 * pad, y + 40)


def pill_anchor(box, tgt):
    x0, y0, x1, y1 = box
    pcx = (x0 + x1) / 2
    sx = x0 if tgt[0] < pcx else x1
    sy = max(y0, min(y1, tgt[1]))
    return (sx, sy)


def dashed(start, end, color, width=3, dash=14, gap=10):
    dxl, dyl = end[0] - start[0], end[1] - start[1]
    dist = math.hypot(dxl, dyl)
    if dist == 0:
        return
    ux, uy = dxl / dist, dyl / dist
    pos = 0.0
    while pos < dist:
        seg = min(dash, dist - pos)
        a = (start[0] + ux * pos, start[1] + uy * pos)
        b = (start[0] + ux * (pos + seg), start[1] + uy * (pos + seg))
        d.line([a, b], fill=color, width=width)
        pos += dash + gap
    ang = math.atan2(dyl, dxl)
    for off in (math.radians(26), math.radians(-26)):
        hx = end[0] - 16 * math.cos(ang - off)
        hy = end[1] - 16 * math.sin(ang - off)
        d.line([end, (hx, hy)], fill=color, width=width)


def mid(a, b):
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)


# --- FLAT drops: one small S# chip per face, colored by simulation status.
# S1=Top(1) S2=Front(2) S3=Bottom(3) S4=Back(4) S5=Left(5) S6=Right(6)
# Simulation drop sequence (only the simulated drops are numbered):
#   Drop 1 = S2, Drop 2 = S3, Drop 3 = S4, Drop 4 = E2-3, Drop 5 = E2-5, Drop 6 = C1-2-6
SIM_SEQ = {"S2": 1, "S3": 2, "S4": 3, "E2-3": 4, "E2-5": 5, "C1-2-6": 6}


def s_chip(cx, cy, label):
    """Chip for a flat drop. Shows 'Drop N  S#' (green) if simulated, else 'S#' (gray)."""
    col = status_color(label)
    if label in SIM_SEQ:
        text = "Drop %d  \u00b7  %s" % (SIM_SEQ[label], label)
    else:
        text = label
    bb = d.textbbox((0, 0), text, font=f_lbl)
    tw = bb[2] - bb[0]
    w, h = tw + 24, 36
    d.rounded_rectangle([cx, cy - h / 2, cx + w, cy + h / 2],
                        radius=18, fill=col, outline=WHITE, width=2)
    t_left(cx + 12, cy, text, f_lbl, WHITE)

# visible faces: chip sits just beside the face badge
s_chip(top_c[0] + 44, top_c[1], "S1")
s_chip(front_c[0] + 42, front_c[1], "S2")
s_chip(right_c[0] + 36, right_c[1], "S6")
# hidden faces: chip sits beside the hollow hidden-face badge
s_chip(bottom_tgt[0] - 30 + 28, bottom_tgt[1] + 150, "S3")
s_chip(back_tgt[0] - 70 - 95, back_tgt[1] - 210 + 54, "S4")   # below badge 4, clear of C1-4-5
s_chip(left_tgt[0] - 290 + 28, left_tgt[1] - 110, "S5")

# --- EDGE drops (faces: 1 Top, 2 Front, 3 Bottom, 4 Back, 5 Left, 6 Right)
# E2-3 = Front & Bottom  -> bottom-front edge  (BFL-BFR)
# E2-5 = Front & Left    -> front-left vertical (TFL-BFL)
# E5-3 = Left & Bottom   -> bottom-left edge    (BFL-BBL)
# E2-3 bottom-front edge (visible BFL-BFR); E2-5 front-left vertical (visible);
# E5-3 bottom-left edge is hidden -> aim just behind the front-left bottom vertex.
edge_targets = {
    "E2-3": mid(BFL, BFR),
    "E2-5": mid(TFL, BFL),
    "E5-3": ((BFL[0] + dx * 0.5), (BFL[1] + dy * 0.5)),
}
edge_label_pos = {
    "E2-3": (120, 870),
    "E2-5": (90, 440),
    "E5-3": (120, 770),
}
def drop_label(prefix, name):
    """'Drop N  Edge drop E2-3' for simulated drops, else 'Edge drop E2-3'."""
    if name in SIM_SEQ:
        return "Drop %d   %s  %s" % (SIM_SEQ[name], prefix, name)
    return "%s  %s" % (prefix, name)


edge_hidden = {"E5-3"}   # bottom-left edge is on the hidden side
for name, tgt in edge_targets.items():
    col = status_color(name)
    box = pill(*edge_label_pos[name], drop_label("Edge drop", name), col)
    if name in edge_hidden:
        dashed(pill_anchor(box, tgt), tgt, col)
    else:
        arrow(pill_anchor(box, tgt), tgt, col)
    d.ellipse([tgt[0] - 6, tgt[1] - 6, tgt[0] + 6, tgt[1] + 6], fill=col)

# --- CORNER drops (vertices where 3 faces meet)
# C1-2-6 = Top+Front+Right  -> TFR
# C1-4-5 = Top+Back+Left    -> TBL
# C2-3-5 = Front+Bottom+Left-> BFL
# C3-4-5 = Bottom+Back+Left -> BBL
corner_targets = {
    "C1-2-6": TFR,     # top-front-right  (visible)
    "C1-4-5": TBL,     # top-back-left    (visible)
    "C2-3-5": BFL,     # front-bottom-left(visible)
    "C3-4-5": BBL,     # back-bottom-left (hidden)
}
corner_hidden = {"C3-4-5"}   # draw with a dashed arrow
corner_label_pos = {
    "C1-2-6": (1120, 470),   # wider "Drop 6  Corner drop C1-2-6" label -> shift left to fit
    "C1-4-5": (980, 150),
    "C2-3-5": (90, 650),
    "C3-4-5": (1230, 790),
}
for name, tgt in corner_targets.items():
    col = status_color(name)
    box = pill(*corner_label_pos[name], drop_label("Corner drop", name), col)
    if name in corner_hidden:
        dashed(pill_anchor(box, tgt), tgt, col)
    else:
        arrow(pill_anchor(box, tgt), tgt, col)
    d.ellipse([tgt[0] - 7, tgt[1] - 7, tgt[0] + 7, tgt[1] + 7], fill=col,
              outline=WHITE, width=2)

# ------------------------------------------------------------ legend
ly, lx = 915, 50
for label, col in [("Used for drop-test simulation (S2, S3, S4, E2-3, E2-5, C1-2-6)", SIM_GREEN),
                   ("Physical test only", NONSIM_GRAY)]:
    d.rounded_rectangle([lx, ly, lx + 26, ly + 26], radius=6, fill=col)
    t_left(lx + 36, ly + 13, label, f_leg, GRAY)
    bb = d.textbbox((0, 0), label, font=f_leg)
    lx += 36 + (bb[2] - bb[0]) + 60

t_left(50, 958,
       "Faces: 1 Top  \u00b7  2 Front  \u00b7  3 Bottom  \u00b7  4 Back  \u00b7  5 Left  \u00b7  "
       "6 Right  (S# = flat drop on that face).   Opposite pairs: 1\u21943, 2\u21944, 6\u21945.",
       f_foot, GRAY)
t_left(50, 980,
       "E/C = intersecting faces (e.g. E2-3 = edge of faces 2 & 3; C1-2-6 = corner of "
       "faces 1, 2 & 6).   Dashed arrow / hollow badge = point or face on the hidden side.",
       f_foot, GRAY)
t_left(W - 150, 50, "ERICSSON", f_sub, WHITE)

out = sys.argv[1] if len(sys.argv) > 1 else "NEBS_Drop_Test_Box.png"
img.save(out, "PNG")
print("Saved:", out, img.size)
