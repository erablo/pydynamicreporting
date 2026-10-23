"""
Graphical view: AI-agent-driven design flow for packaging materials.

Layout:
  - Top band: title
  - Orchestrator (supervisor) agent across the top
  - 6-stage left-to-right pipeline (Requirements -> Release) with chevrons
  - One AI agent card under each stage
  - Shared foundation bar: Knowledge Base / RAG + tools (Ansys/LS-Dyna, PLM, M&L)
  - Feedback loop arrow (simulation <-> verification)
Ericsson / Templafy Atlas styling. Procedurally drawn -> no external assets.
"""

from PIL import Image, ImageDraw, ImageFont
import sys, math

# ------------------------------------------------------------ palette
ERICSSON_BLUE = (0x00, 0x30, 0x56)
ACCENT = (0x00, 0x82, 0xF0)
TEAL = (0x00, 0xA9, 0xA5)
PURPLE = (0x7A, 0x2B, 0x8E)
GREEN = (0x1E, 0xA3, 0x4E)
AMBER = (0xE6, 0x8A, 0x00)
GRAY = (0x53, 0x53, 0x5A)
LIGHT = (0xF2, 0xF2, 0xF4)
MIDGRAY = (0xC7, 0xCD, 0xD4)
WHITE = (0xFF, 0xFF, 0xFF)

W, H = 1920, 1440
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

f_title = font(46, bold=True)
f_sub = font(24)
f_stage = font(23, bold=True)
f_agent = font(22, bold=True)
f_body = font(17)
f_small = font(15)
f_tag = font(16, bold=True)
f_foot = font(16)


def t_center(cx, cy, s, fnt, fill):
    bb = d.textbbox((0, 0), s, font=fnt)
    d.text((cx - (bb[2] - bb[0]) / 2, cy - (bb[3] - bb[1]) / 2 - bb[1]), s, font=fnt, fill=fill)


def t_left(x, cy, s, fnt, fill):
    bb = d.textbbox((0, 0), s, font=fnt)
    d.text((x, cy - (bb[3] - bb[1]) / 2 - bb[1]), s, font=fnt, fill=fill)


def wrap(text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        test = (cur + " " + w_).strip()
        if d.textbbox((0, 0), test, font=fnt)[2] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def para(x, y, text, fnt, fill, max_w, lh=22):
    for i, ln in enumerate(wrap(text, fnt, max_w)):
        t_left(x, y + i * lh, ln, fnt, fill)
    return y + len(wrap(text, fnt, max_w)) * lh


# ------------------------------------------------------------ title band
d.rectangle([0, 0, W, 118], fill=ERICSSON_BLUE)
d.rectangle([0, 112, W, 118], fill=ACCENT)
t_left(54, 44, "Packaging Material Design Flow \u2013 AI Agent Architecture", f_title, WHITE)
t_left(56, 92, "Agentic workflow from requirements to release \u00b7 PMD", f_sub,
       (0xBF, 0xD9, 0xF2))
t_left(W - 170, 52, "ERICSSON", f_sub, WHITE)


# ------------------------------------------------------------ Anark interface bar
anark_x0, anark_y0, anark_x1, anark_y1 = 54, 224, W - 54, 290
d.rounded_rectangle([anark_x0, anark_y0, anark_x1, anark_y1], radius=16, fill=TEAL)
# agent (robot) glyph on the left -> Anark is itself an agent
gx, gy = anark_x0 + 40, (anark_y0 + anark_y1) / 2
d.rounded_rectangle([gx - 15, gy - 12, gx + 15, gy + 14], radius=5, fill=WHITE)
d.ellipse([gx - 8, gy - 4, gx - 1, gy + 3], fill=TEAL)
d.ellipse([gx + 1, gy - 4, gx + 8, gy + 3], fill=TEAL)
d.line([gx - 6, gy + 8, gx + 6, gy + 8], fill=TEAL, width=2)
d.line([gx, gy - 12, gx, gy - 20], fill=WHITE, width=3)
d.ellipse([gx - 4, gy - 25, gx + 4, gy - 17], fill=WHITE)
t_left(anark_x0 + 78, anark_y0 + 22,
       "Anark/Windchill Interface Agent \u2013 User Interface & Collaboration Layer",
       f_agent, WHITE)
t_left(anark_x0 + 78, anark_y0 + 46,
       "agentic single pane for the team: visualize & review 3D CAD, comment/approve, publish reports \u2013 front-end to every agent",
       f_small, (0xE6, 0xF6, 0xF5))

# MCP server badge on the right of the Anark bar
mcp_label = "MCP server"
mbb = d.textbbox((0, 0), mcp_label, font=f_tag)
mtw = mbb[2] - mbb[0]
mcp_w = mtw + 54
mcp_x1 = anark_x1 - 20
mcp_x0 = mcp_x1 - mcp_w
mcp_cy = (anark_y0 + anark_y1) / 2
d.rounded_rectangle([mcp_x0, mcp_cy - 20, mcp_x1, mcp_cy + 20], radius=20, fill=WHITE,
                    outline=WHITE, width=0)
# plug / connector glyph
pgx, pgy = mcp_x0 + 24, mcp_cy
d.rounded_rectangle([pgx - 9, pgy - 7, pgx + 7, pgy + 7], radius=2, fill=TEAL)
d.line([pgx + 7, pgy - 3, pgx + 14, pgy - 3], fill=TEAL, width=3)
d.line([pgx + 7, pgy + 3, pgx + 14, pgy + 3], fill=TEAL, width=3)
t_left(mcp_x0 + 44, mcp_cy, mcp_label, f_tag, TEAL)
# connector line from the agent body to the MCP badge
d.line([(mcp_x0 - 14, mcp_cy), (mcp_x0, mcp_cy)], fill=WHITE, width=3)

# ------------------------------------------------------------ orchestrator (now on top)
orch_x0, orch_y0, orch_x1, orch_y1 = 300, 132, 1620, 198
d.rounded_rectangle([orch_x0, orch_y0, orch_x1, orch_y1], radius=16, fill=ERICSSON_BLUE)
t_center((orch_x0 + orch_x1) / 2, (orch_y0 + orch_y1) / 2 - 12,
         "Orchestrator Agent  (Supervisor)", f_agent, WHITE)
t_center((orch_x0 + orch_x1) / 2, (orch_y0 + orch_y1) / 2 + 16,
         "plans tasks \u00b7 routes between agents \u00b7 maintains state \u00b7 human-in-the-loop checkpoints",
         f_small, (0xBF, 0xD9, 0xF2))
# Orchestrator connects down to the Anark/Windchill interface bar
d.line([((orch_x0 + orch_x1) / 2, orch_y1), ((orch_x0 + orch_x1) / 2, anark_y0)],
       fill=MIDGRAY, width=2)


# ------------------------------------------------------------ pipeline stages
stages = [
    ("1", "Requirements\n& Intake", ACCENT,
     "Parse inputs \u2013 PDA & Packaging Requirements: weight, dimensions, sustainability target (plastic %), compliance needs."),
    ("2", "Concept &\nMaterial Selection", TEAL,
     "Propose fiber / molded-pulp / corrugated concepts per Building Practice & Sustainability req's; recommend qualities & suppliers."),
    ("3", "Geometry &\nCAD Modeling", PURPLE,
     "Generate box & fitment geometry, folding schedules; review & validate CAD in Anark before meshing."),
    ("4", "Drop-Test\nSimulation", GREEN,
     "Set up Ansys / LS-Dyna drops (6-drop template), material cards, predict G-values."),
    ("5", "Verification\n& Correlation", AMBER,
     "Correlate simulation vs. physical results; flag gaps & iterate."),
    ("6", "Release &\nDocumentation", ERICSSON_BLUE,
     "HWDP release, marking & labelling, material declarations, reusable templates."),
]

agents = [
    "Requirements Agent",
    "Material-Selection Agent",
    "CAD / Geometry Agent",
    "Simulation Agent",
    "Correlation Agent",
    "Compliance & Docs Agent",
]

n = len(stages)
margin = 54
gap = 20
band_x0 = margin
band_x1 = W - margin
col_w = (band_x1 - band_x0 - gap * (n - 1)) / n

chev_y0, chev_y1 = 300, 384       # stage chevron band
chev_h = chev_y1 - chev_y0
notch = 26

agent_y0, agent_y1 = 430, 712     # agent card band (taller to fit extra test chips)


def chevron(x0, y0, x1, y1, color, first=False, last=False):
    nn = 0 if first else notch
    pts = [(x0, y0), (x1 - notch, y0), (x1, (y0 + y1) / 2), (x1 - notch, y1),
           (x0, y1), (x0 + nn, (y0 + y1) / 2)]
    if last:
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0 + nn, (y0 + y1) / 2)]
    d.polygon(pts, fill=color)


centers = []
for i, (no, name, color, desc) in enumerate(stages):
    x0 = band_x0 + i * (col_w + gap)
    x1 = x0 + col_w
    cx = (x0 + x1) / 2
    centers.append((cx, x0, x1, color))

    # chevron stage header
    chevron(x0, chev_y0, x1, chev_y1, color, first=(i == 0), last=(i == n - 1))
    # stage number disc
    d.ellipse([x0 + 16, chev_y0 + chev_h / 2 - 20, x0 + 56, chev_y0 + chev_h / 2 + 20],
              fill=WHITE)
    t_center(x0 + 36, chev_y0 + chev_h / 2, no, f_stage, color)
    # stage title (wrapped, 2 lines)
    for li, ln in enumerate(name.split("\n")):
        t_center(cx + 24, chev_y0 + chev_h / 2 - 14 + li * 26, ln, f_stage, WHITE)

    # connector from the interface bar (Anark/Windchill) down to each stage
    d.line([(cx, anark_y1), (cx, chev_y0)], fill=MIDGRAY, width=2)

    # agent card
    d.rounded_rectangle([x0, agent_y0, x1, agent_y1], radius=14, fill=WHITE,
                        outline=color, width=3)
    d.rounded_rectangle([x0, agent_y0, x1, agent_y0 + 52], radius=14, fill=color)
    d.rectangle([x0, agent_y0 + 38, x1, agent_y0 + 52], fill=color)
    # robot/agent glyph
    gx, gy = x0 + 26, agent_y0 + 26
    d.rounded_rectangle([gx - 11, gy - 9, gx + 11, gy + 11], radius=4, fill=WHITE)
    d.ellipse([gx - 6, gy - 3, gx - 1, gy + 2], fill=color)
    d.ellipse([gx + 1, gy - 3, gx + 6, gy + 2], fill=color)
    d.line([gx, gy - 9, gx, gy - 16], fill=WHITE, width=2)
    d.ellipse([gx - 3, gy - 20, gx + 3, gy - 14], fill=WHITE)
    for li, ln in enumerate(wrap(agents[i], f_agent, col_w - 70)):
        t_left(x0 + 48, agent_y0 + 20 + li * 24, ln, f_agent, WHITE)
    # connector stage -> agent
    d.line([(cx, chev_y1), (cx, agent_y0)], fill=color, width=3)
    # arrowhead
    d.polygon([(cx - 7, agent_y0 - 10), (cx + 7, agent_y0 - 10), (cx, agent_y0)], fill=color)
    # agent description
    para(x0 + 18, agent_y0 + 74, desc, f_body, GRAY, col_w - 34, lh=22)

    # stage-specific tool / artifact tags (list = stacked from the card bottom upward)
    stage_tags = {
        0: [("PDA \u00b7 Design Assignment", ACCENT, "doc"),
            ("Packaging Requirements", ACCENT, "doc")],
        1: [("Building Practice", TEAL, "doc"),
            ("Sustainability req's", TEAL, "doc")],
        2: [("Anark \u00b7 CAD file review", TEAL, "lens")],
    }
    if i in stage_tags:
        tags = stage_tags[i]
        for ti, (tag, tcol, glyph) in enumerate(tags):
            # stack upward: last tag in list sits at the bottom
            ty0 = agent_y1 - 48 - (len(tags) - 1 - ti) * 46
            tbb = d.textbbox((0, 0), tag, font=f_tag)
            tw = tbb[2] - tbb[0]
            d.rounded_rectangle([x0 + 18, ty0, x0 + 18 + tw + 42, ty0 + 36], radius=18,
                                fill=tcol)
            gx2, gy2 = x0 + 36, ty0 + 18
            if glyph == "lens":          # magnifier (review)
                d.ellipse([gx2 - 8, gy2 - 8, gx2 + 4, gy2 + 4], outline=WHITE, width=3)
                d.line([gx2 + 3, gy2 + 3, gx2 + 9, gy2 + 9], fill=WHITE, width=3)
            else:                         # document (artifact)
                d.rounded_rectangle([gx2 - 7, gy2 - 9, gx2 + 7, gy2 + 9], radius=2, fill=WHITE)
                for yy in (-4, 0, 4):
                    d.line([gx2 - 4, gy2 + yy, gx2 + 4, gy2 + yy], fill=tcol, width=1)
            t_left(x0 + 18 + 32, ty0 + 18, tag, f_tag, WHITE)

    # Correlation agent (stage 5 / index 4): physical tests fed into correlation
    if i == 4:
        t_left(x0 + 18, agent_y0 + 132, "Tests & calc. correlated:", f_small, GRAY)
        chips = ["Drop test", "Vibration test", "Compression test",
                 "BCT calculation", "BCT test"]
        cxp, cyp = x0 + 18, agent_y0 + 154
        for ch in chips:
            cbb = d.textbbox((0, 0), ch, font=f_tag)
            cw = cbb[2] - cbb[0] + 26
            if cxp + cw > x1 - 14:          # wrap to next row inside the card
                cxp = x0 + 18
                cyp += 42
            d.rounded_rectangle([cxp, cyp, cxp + cw, cyp + 34], radius=17, fill=AMBER)
            t_left(cxp + 13, cyp + 17, ch, f_tag, WHITE)
            cxp += cw + 10

    # MCP-server badge helper
    def mcp_badge(bx, by, col):
        mlabel = "MCP server"
        mbb2 = d.textbbox((0, 0), mlabel, font=f_tag)
        mw2 = mbb2[2] - mbb2[0] + 54
        d.rounded_rectangle([bx, by, bx + mw2, by + 36], radius=18, fill=col)
        pgx, pgy = bx + 18, by + 18
        d.rounded_rectangle([pgx - 9, pgy - 7, pgx + 7, pgy + 7], radius=2, fill=WHITE)
        d.line([pgx + 7, pgy - 3, pgx + 15, pgy - 3], fill=WHITE, width=3)
        d.line([pgx + 7, pgy + 3, pgx + 15, pgy + 3], fill=WHITE, width=3)
        t_left(bx + 44, by + 18, mlabel, f_tag, WHITE)

    # Simulation agent (stage 4 / index 3): connects to simulation tools via MCP
    if i == 3:
        mcp_badge(x0 + 18, agent_y1 - 48, GREEN)

    # CAD / Geometry agent (stage 3 / index 2): MCP badge above the Anark review tag
    if i == 2:
        mcp_badge(x0 + 18, agent_y1 - 48 - 46, PURPLE)

    # Compliance & Docs agent (stage 6 / index 5): MCP + REST badges + connected systems
    if i == 5:
        mcp_badge(x0 + 18, agent_y0 + 128, ERICSSON_BLUE)
        # REST API badge next to the MCP badge
        mlbl = "MCP server"
        mw = d.textbbox((0, 0), mlbl, font=f_tag)[2] + 54
        rlabel = "REST API"
        rbb = d.textbbox((0, 0), rlabel, font=f_tag)
        rw = rbb[2] - rbb[0] + 48
        rbx = x0 + 18 + mw + 12
        rby = agent_y0 + 128
        d.rounded_rectangle([rbx, rby, rbx + rw, rby + 36], radius=18, fill=WHITE,
                            outline=ERICSSON_BLUE, width=2)
        # braces glyph { }
        t_left(rbx + 14, rby + 18, "{ }", f_tag, ERICSSON_BLUE)
        t_left(rbx + 40, rby + 18, rlabel, f_tag, ERICSSON_BLUE)
        t_left(x0 + 18, agent_y0 + 184, "Connected via MCP / REST API:", f_small, GRAY)
        sys_chips = ["PRIM", "Eliza", "Eridoc", "Erimate"]
        sxp, syp = x0 + 18, agent_y0 + 204
        for sc in sys_chips:
            sbb = d.textbbox((0, 0), sc, font=f_tag)
            sw = sbb[2] - sbb[0] + 26
            if sxp + sw > x1 - 14:
                sxp = x0 + 18
                syp += 42
            d.rounded_rectangle([sxp, syp, sxp + sw, syp + 34], radius=17, fill=WHITE,
                                outline=ERICSSON_BLUE, width=2)
            t_left(sxp + 13, syp + 17, sc, f_tag, ERICSSON_BLUE)
            sxp += sw + 10


# ------------------------------------------------------------ feedback loop (Correlation -> CAD/Geometry)
cx_src = centers[4][0]   # Correlation agent
cx_dst = centers[1][0]   # Material-Selection agent
loop_y = agent_y1 + 46
d.line([(cx_src, agent_y1), (cx_src, loop_y)], fill=AMBER, width=3)
d.line([(cx_src, loop_y), (cx_dst, loop_y)], fill=AMBER, width=3)
d.line([(cx_dst, loop_y), (cx_dst, agent_y1)], fill=AMBER, width=3)
d.polygon([(cx_dst - 7, agent_y1 + 10), (cx_dst + 7, agent_y1 + 10), (cx_dst, agent_y1)],
          fill=AMBER)
t_center((cx_dst + cx_src) / 2, loop_y + 18,
         "iterate material / design \u00b7 re-simulate on correlation gap", f_small, AMBER)


# ------------------------------------------------------------ shared Documentation Agent band
doc_y0, doc_y1 = 826, 980
d.rounded_rectangle([margin, doc_y0, W - margin, doc_y1], radius=16, fill=WHITE,
                    outline=ERICSSON_BLUE, width=3)
d.rounded_rectangle([margin, doc_y0, margin + 300, doc_y1], radius=16, fill=ERICSSON_BLUE)
d.rectangle([margin + 150, doc_y0, margin + 300, doc_y1], fill=ERICSSON_BLUE)
# agent glyph
gx, gy = margin + 44, doc_y0 + 44
d.rounded_rectangle([gx - 13, gy - 11, gx + 13, gy + 13], radius=4, fill=WHITE)
d.ellipse([gx - 7, gy - 4, gx - 1, gy + 2], fill=ERICSSON_BLUE)
d.ellipse([gx + 1, gy - 4, gx + 7, gy + 2], fill=ERICSSON_BLUE)
d.line([gx, gy - 11, gx, gy - 19], fill=WHITE, width=2)
d.ellipse([gx - 3, gy - 23, gx + 3, gy - 17], fill=WHITE)
t_left(margin + 72, doc_y0 + 30, "Documentation", f_agent, WHITE)
t_left(margin + 72, doc_y0 + 58, "Agent  (shared)", f_agent, WHITE)
t_left(margin + 20, doc_y1 - 30, "generates from templates", f_small, (0xBF, 0xD9, 0xF2))

# document template chips
docs = [
    "IP \u2013 Implementation Proposal",
    "NDS \u2013 Node Design Specification",
    "PDA \u2013 Design Assignment",
    "Verification Report",
    "Packaging Instruction",
    "1301 Drawing",
    "PPWR DoC",
]
dx = margin + 340
dy_row0 = doc_y0 + 28
row_h = 54
dyr = dy_row0
for label in docs:
    bb = d.textbbox((0, 0), label, font=f_tag)
    tw = bb[2] - bb[0]
    chip_w = tw + 56
    if dx + chip_w > W - margin - 24:
        dx = margin + 340
        dyr += row_h
    d.rounded_rectangle([dx, dyr, dx + chip_w, dyr + 42], radius=10, fill=LIGHT,
                        outline=ERICSSON_BLUE, width=2)
    # doc glyph
    ix, iy = dx + 22, dyr + 21
    d.rounded_rectangle([ix - 9, iy - 12, ix + 9, iy + 12], radius=2, fill=WHITE,
                        outline=ERICSSON_BLUE, width=2)
    for yy in (-5, 0, 5):
        d.line([ix - 5, iy + yy, ix + 5, iy + yy], fill=ACCENT, width=1)
    t_left(dx + 42, dyr + 21, label, f_tag, ERICSSON_BLUE)
    dx += chip_w + 18

# connect the stage agents down into the documentation band
for cx, x0, x1, color in centers:
    d.line([(cx, agent_y1 + 2), (cx, doc_y0)], fill=MIDGRAY, width=1)


# ------------------------------------------------------------ shared Review Agent band
rev_y0, rev_y1 = 1000, 1104
d.rounded_rectangle([margin, rev_y0, W - margin, rev_y1], radius=16, fill=WHITE,
                    outline=TEAL, width=3)
d.rounded_rectangle([margin, rev_y0, margin + 300, rev_y1], radius=16, fill=TEAL)
d.rectangle([margin + 150, rev_y0, margin + 300, rev_y1], fill=TEAL)
# agent glyph
rgx, rgy = margin + 44, rev_y0 + 40
d.rounded_rectangle([rgx - 13, rgy - 11, rgx + 13, rgy + 13], radius=4, fill=WHITE)
d.ellipse([rgx - 7, rgy - 4, rgx - 1, rgy + 2], fill=TEAL)
d.ellipse([rgx + 1, rgy - 4, rgx + 7, rgy + 2], fill=TEAL)
d.line([rgx, rgy - 11, rgx, rgy - 19], fill=WHITE, width=2)
d.ellipse([rgx - 3, rgy - 23, rgx + 3, rgy - 17], fill=WHITE)
t_left(margin + 72, rev_y0 + 26, "Review Agent", f_agent, WHITE)
t_left(margin + 72, rev_y0 + 54, "(shared)", f_agent, WHITE)
t_left(margin + 20, rev_y1 - 28, "automated design review", f_small, (0xE6, 0xF6, 0xF5))

reviews = [
    "2D drawing review",
    "3D model / drawing review",
    "Compliance vs. requirements",
    "PPWR review",
    "Pallet Pattern Opt.",
]
rx = margin + 340
ryr = rev_y0 + 32
chip_boxes = {}      # label -> (x0, y0, x1, y1) for building an HTML image map
for label in reviews:
    bb = d.textbbox((0, 0), label, font=f_tag)
    tw = bb[2] - bb[0]
    chip_w = tw + 56
    d.rounded_rectangle([rx, ryr, rx + chip_w, ryr + 42], radius=10, fill=LIGHT,
                        outline=TEAL, width=2)
    # magnifier glyph (review)
    mx, my = rx + 24, ryr + 21
    d.ellipse([mx - 9, my - 9, mx + 3, my + 3], outline=TEAL, width=3)
    d.line([mx + 2, my + 2, mx + 9, my + 9], fill=TEAL, width=3)
    t_left(rx + 42, ryr + 21, label, f_tag, ERICSSON_BLUE)
    chip_boxes[label] = (int(rx), int(ryr), int(rx + chip_w), int(ryr + 42))
    rx += chip_w + 18

# write the Pallet Pattern Opt. chip bounds for the HTML wrapper / image map
with open("review_chip_coords.txt", "w") as _f:
    _x0, _y0, _x1, _y1 = chip_boxes["Pallet Pattern Opt."]
    _f.write("%d,%d,%d,%d,%d,%d" % (_x0, _y0, _x1, _y1, W, H))

# Review Agent draws on Anark + requirements; link it to the CAD stage & requirements stage
d.line([(centers[0][0], doc_y1), (centers[0][0], rev_y0)], fill=MIDGRAY, width=1)
d.line([(centers[2][0], doc_y1), (centers[2][0], rev_y0)], fill=MIDGRAY, width=1)


# ------------------------------------------------------------ shared foundation bar
found_y0 = 1140
found_y1 = 1300
d.rounded_rectangle([margin, found_y0, W - margin, found_y1], radius=16, fill=LIGHT,
                    outline=ERICSSON_BLUE, width=2)
t_left(margin + 28, found_y0 + 30, "Shared foundation", f_agent, ERICSSON_BLUE)

tools = [
    ("Anark/Windchill Agent (interface & CAD review)", TEAL),
    ("Creo CAD", PURPLE),
    ("CDPH", ERICSSON_BLUE),
    ("Knowledge Base / RAG", GRAY),
    ("Material & G-value library", GREEN),
    ("Ansys \u00b7 LS-Dyna", PURPLE),
    ("PLM / HWDP", ACCENT),
    ("Marking & Labelling rules", AMBER),
    ("Supplier data (DS Smith, Nefab)", GRAY),
]
tx = margin + 320
trow = 0
chip_row_h = 56
for label, col in tools:
    bb = d.textbbox((0, 0), label, font=f_tag)
    tw = bb[2] - bb[0]
    chip_w = tw + 40
    if tx + chip_w > W - margin - 20:     # wrap to next row
        tx = margin + 320
        trow += 1
    cy0 = found_y0 + 40 + trow * chip_row_h
    d.rounded_rectangle([tx, cy0, tx + chip_w, cy0 + 44], radius=22,
                        fill=WHITE, outline=col, width=3)
    d.ellipse([tx + 14, cy0 + 16, tx + 26, cy0 + 28], fill=col)
    t_left(tx + 34, cy0 + 22, label, f_tag, GRAY)
    tx += chip_w + 20

# ------------------------------------------------------------ legend / footer
t_left(margin, 1342,
       "Shared agents: Documentation Agent generates IP, NDS, PDA, Verification Report & "
       "Packaging Instruction from templates. Review Agent reviews 2D/3D drawings and "
       "checks compliance vs. requirements.", f_foot, GRAY)
t_left(margin, 1372,
       "Each stage is run by a specialized AI agent, coordinated by the Orchestrator; "
       "agents read/write a shared knowledge base and call external tools.", f_foot, GRAY)
t_left(margin, 1406, "Ericsson Internal  \u00b7  PMD  \u00b7  Packaging Simulation Pre-Dev",
       f_small, MIDGRAY)

out = sys.argv[1] if len(sys.argv) > 1 else "Packaging_AI_Agent_Design_Flow.png"
img.save(out, "PNG")
print("Saved:", out, img.size)
