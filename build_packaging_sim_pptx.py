"""
Generate a PowerPoint summary of the Packaging Simulation Pilot (Ansys / LS-Dyna).

Styling follows the Ericsson / Templafy "Atlas" template conventions used in the
source report (title slide, "Ericsson Internal" security class, footer with
signum / revision / date, Ericsson color palette). Run Templafy's
"Apply / Refresh template" inside PowerPoint afterwards to bind the official
branded master if required.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# ---------------------------------------------------------------- brand palette
ERICSSON_BLUE = RGBColor(0x00, 0x30, 0x56)   # deep blue (primary)
ERICSSON_ACCENT = RGBColor(0x00, 0x82, 0xF0)  # bright blue accent
ERICSSON_GRAY = RGBColor(0x53, 0x53, 0x5A)   # body gray
LIGHT_GRAY = RGBColor(0xF2, 0xF2, 0xF4)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
TEAL = RGBColor(0x00, 0xA9, 0xA5)

FONT = "Arial"  # Templafy/Ericsson Atlas body font

PREPARED = "ERABLO Anders Blom"
REVISION = "PA1"
DATE = "2025-11-18"
SECURITY = "Ericsson Internal"

prs = Presentation()
prs.slide_width = Inches(13.333)   # 16:9 widescreen
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

SW = prs.slide_width
SH = prs.slide_height


# ------------------------------------------------------------------- helpers
def add_rect(slide, x, y, w, h, color, line=False):
    from pptx.enum.shapes import MSO_SHAPE
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    if line:
        shp.line.color.rgb = color
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def add_text(slide, x, y, w, h, text, size, color=ERICSSON_GRAY, bold=False,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font=FONT, italic=False):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = ln
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.name = font
        r.font.color.rgb = color
    return tb


def add_footer(slide, page_no):
    # thin accent rule above footer
    add_rect(slide, Inches(0.5), Inches(7.02), Inches(12.33), Pt(1), ERICSSON_ACCENT)
    footer = f"{PREPARED}  |  {REVISION}  |  {DATE}  |  {SECURITY}  |  Page {page_no} of 11"
    add_text(slide, Inches(0.5), Inches(7.08), Inches(12.33), Inches(0.3),
             footer, 8, ERICSSON_GRAY, align=PP_ALIGN.LEFT)


def content_header(slide, title, page_no):
    add_rect(slide, 0, 0, SW, Inches(1.1), WHITE)
    add_rect(slide, Inches(0.5), Inches(0.35), Inches(0.12), Inches(0.55), ERICSSON_ACCENT)
    add_text(slide, Inches(0.75), Inches(0.3), Inches(11.5), Inches(0.7),
             title, 26, ERICSSON_BLUE, bold=True)
    add_rect(slide, Inches(0.5), Inches(1.05), Inches(12.33), Pt(1.5), LIGHT_GRAY)
    add_footer(slide, page_no)


def add_table(slide, x, y, w, headers, rows, col_widths, header_color=ERICSSON_BLUE,
              body_size=10, header_size=10, row_h=0.3):
    n_rows = len(rows) + 1
    n_cols = len(headers)
    h = Inches(row_h * n_rows)
    gtbl = slide.shapes.add_table(n_rows, n_cols, x, y, w, h).table
    for ci, cw in enumerate(col_widths):
        gtbl.columns[ci].width = cw
    # header
    for ci, head in enumerate(headers):
        cell = gtbl.cell(0, ci)
        cell.fill.solid()
        cell.fill.fore_color.rgb = header_color
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        r = p.add_run(); r.text = head
        r.font.size = Pt(header_size); r.font.bold = True
        r.font.color.rgb = WHITE; r.font.name = FONT
        p.alignment = PP_ALIGN.LEFT
    # body
    for ri, row in enumerate(rows, start=1):
        for ci, val in enumerate(row):
            cell = gtbl.cell(ri, ci)
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if ri % 2 else LIGHT_GRAY
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run(); r.text = str(val)
            r.font.size = Pt(body_size)
            r.font.color.rgb = ERICSSON_GRAY; r.font.name = FONT
            bold = (ci == len(row) - 1 and str(row[0]).lower().startswith("total")) or \
                   (str(row[0]).lower().startswith("total"))
            r.font.bold = bool(bold)
            p.alignment = PP_ALIGN.LEFT
    return gtbl


def bullets(slide, x, y, w, h, items, size=14, color=ERICSSON_GRAY, gap=6):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, (txt, lvl) in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = lvl
        p.space_after = Pt(gap)
        marker = "\u2022  " if lvl == 0 else "\u2013  "
        r = p.add_run()
        r.text = marker + txt
        r.font.size = Pt(size - lvl * 2)
        r.font.name = FONT
        r.font.color.rgb = ERICSSON_BLUE if lvl == 0 else color
        r.font.bold = (lvl == 0)
    return tb


# ============================================================= SLIDE 1 - TITLE
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, SW, SH, ERICSSON_BLUE)
add_rect(s, 0, Inches(4.9), SW, Inches(0.08), ERICSSON_ACCENT)
add_rect(s, Inches(0.9), Inches(2.0), Inches(0.18), Inches(2.4), TEAL)
add_text(s, Inches(1.25), Inches(2.0), Inches(10.8), Inches(1.9),
         "Packaging Simulation Pilot", 44, WHITE, bold=True)
add_text(s, Inches(1.25), Inches(3.25), Inches(10.8), Inches(0.8),
         "Ansys \u2013 LS-Dyna  |  Summary", 24, RGBColor(0xBF, 0xD9, 0xF2))
add_text(s, Inches(1.25), Inches(5.15), Inches(10.8), Inches(1.4),
         "Anders Blom \u2013 PMD\nLucia Alhalabi \u2013 PMD\n"
         "Peter Tiefenthaler \u2013 EAS Sim\nAndreas Ankarbj\u00f6rk \u2013 Mech Design Sim",
         14, WHITE)
add_text(s, Inches(0.9), Inches(6.9), Inches(11.5), Inches(0.4),
         f"{SECURITY}   |   {REVISION}   |   {DATE}   |   Prepared by {PREPARED}",
         10, RGBColor(0x9F, 0xC2, 0xE8))
add_text(s, Inches(11.0), Inches(0.4), Inches(1.9), Inches(0.4),
         "ERICSSON", 16, WHITE, bold=True, align=PP_ALIGN.RIGHT)

# =========================================================== SLIDE 2 - JOURNEY
s = prs.slides.add_slide(BLANK)
content_header(s, "Packaging Simulation Journey", 2)
phases = [
    ("RFI Prep", "2024-04", TEAL),
    ("RFI", "2024-08", TEAL),
    ("PoC", "2025-01", ERICSSON_ACCENT),
    ("Pilot Prep", "2025-02", ERICSSON_ACCENT),
    ("Pilot", "2025-Q4", ERICSSON_BLUE),
    ("Pre-dev 1", "2026-Q2", ERICSSON_GRAY),
    ("Pre-dev 2", "2026-Q3", ERICSSON_GRAY),
    ("Deploy", "Planned", RGBColor(0xA0, 0xA0, 0xA8)),
]
n = len(phases)
total_w = Inches(12.0)
gap = Inches(0.15)
box_w = Emu(int((total_w - gap * (n - 1)) / n))
y = Inches(2.6)
x = Inches(0.66)
for i, (name, when, col) in enumerate(phases):
    bx = Emu(int(x) + i * (int(box_w) + int(gap)))
    add_rect(s, bx, y, box_w, Inches(1.0), col)
    add_text(s, bx, Inches(2.75), box_w, Inches(0.7), name, 12, WHITE, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, bx, Inches(3.75), box_w, Inches(0.3), when, 9, ERICSSON_GRAY,
             align=PP_ALIGN.CENTER)
add_text(s, Inches(0.66), Inches(4.6), Inches(12.0), Inches(1.6),
         "Tool evaluation across Ansys, Altair, Dassault and Keysight (RFI) narrowed to "
         "Ansys \u2013 LS-Dyna via RFQ & technical evaluation.\n"
         "PoC and Pilot ran on free-of-charge (FoC) Ansys LS-Dyna licenses. A license "
         "purchase decision follows the pilot, with pre-development activities continuing "
         "into 2026 ahead of deployment.", 13, ERICSSON_GRAY)

# ====================================================== SLIDE 3 - PURPOSE/BG
s = prs.slides.add_slide(BLANK)
content_header(s, "Purpose & Background", 3)
bullets(s, Inches(0.75), Inches(1.5), Inches(11.8), Inches(5.2), [
    ("Fulfil Ericsson's 2030 sustainability goal of only 2% plastic content (RTE OKR)", 0),
    ("Future packaging will require more expensive molding tools, increasing the need "
     "for simulation before tool ordering", 0),
    ("Establish procedures for performing drop-test simulations on packaging materials", 0),
    ("Create models and ways of working (WoW) for simulation of fiber paper", 0),
    ("Virtual-lab methodology to generate material properties", 1),
    ("Leverage Ansys knowledge and experience acquired from the PoC for application at Ericsson", 0),
    ("Learn how to use the LS-Dyna tool", 0),
], size=16, gap=12)

# =================================================== SLIDE 4 - OUTCOME/STATUS
s = prs.slides.add_slide(BLANK)
content_header(s, "Status / Outcome \u2013 Pilot", 4)
add_text(s, Inches(0.75), Inches(1.3), Inches(5.6), Inches(0.4),
         "Replanning was required due to:", 14, ERICSSON_BLUE, bold=True)
bullets(s, Inches(0.75), Inches(1.75), Inches(5.7), Inches(2.6), [
    ("Loss of Mech Design support resource during a large part of the pilot", 0),
    ("New inputs from supplier Ansys on project approach", 0),
    ("Templates, automation, sequential drops, improved simulation-model setups", 1),
    ("Simulation of the Radio product moved until after the pilot", 0),
], size=12, gap=6)
add_text(s, Inches(6.7), Inches(1.3), Inches(6.0), Inches(0.4),
         "Pilot delivered:", 14, ERICSSON_BLUE, bold=True)
bullets(s, Inches(6.7), Inches(1.75), Inches(6.0), Inches(5.0), [
    ("Virtual-lab WoW (phenomenological model) for fiber materials as simulation input", 0),
    ("Recommended 6 drops instead of 24 (ASTM + NEBS) on defined sides, corners & edges", 0),
    ("Defined how to obtain the fiber geometry model from suppliers", 0),
    ("Knowledge to set up a full simulation model: geometry, material data, meshing, "
     "boundaries, result trackers", 0),
    ("Reusable simulation template for new simulations", 0),
    ("Focused on 19-inch Base Band with plastic fitments", 0),
    ("3D model created from a 2D drawing in Ansys Discovery (step-file issue)", 1),
], size=12, gap=6)

# ===================================================== SLIDE 5 - VIRTUAL LAB
s = prs.slides.add_slide(BLANK)
content_header(s, "The Virtual Lab \u2013 Fiber Material Workflow", 5)
steps = [
    "Tensile\nmeasurements",
    "Create material\ncard MAT_PAPER",
    "Verify with\nLS-Dyna sim",
    "Convert to MAT_058\n(HD & LD sim model)",
    "Use MAT_058\nin simulation",
]
tools = ["", "Excel & LS-Dyna", "LS-Dyna", "Excel & LS-Dyna", "Material properties"]
n = len(steps)
bw = Inches(2.25)
y = Inches(2.7)
startx = Inches(0.5)
gapx = Inches(0.18)
for i, st in enumerate(steps):
    bx = Emu(int(startx) + i * (int(bw) + int(gapx)))
    col = ERICSSON_ACCENT if i % 2 == 0 else ERICSSON_BLUE
    add_rect(s, bx, y, bw, Inches(1.2), col)
    add_text(s, bx, y, bw, Inches(1.2), st, 12, WHITE, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    if tools[i]:
        add_text(s, bx, Inches(4.05), bw, Inches(0.5), tools[i], 10, ERICSSON_GRAY,
                 align=PP_ALIGN.CENTER)
    if i < n - 1:
        ax = Emu(int(bx) + int(bw) + int(gapx) // 4)
        add_text(s, ax, y, Inches(0.2), Inches(1.2), "\u2192", 20, TEAL,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, Inches(0.75), Inches(5.0), Inches(11.8), Inches(1.6),
         "Material-model variants explored: (1) Layered Shell, (2) Shell and Solid, (3) Shell.\n"
         "Tensile test data is converted to plastic strain & stress, calculated in Excel, then "
         "validated with LS-Dyna before the material model is used in the high-detail (HD) model "
         "and aligned down to the low-detail (LD) model. MAT_58 is the material data used in the "
         "final simulation model.", 13, ERICSSON_GRAY)

# ================================================= SLIDE 6 - COST SAVINGS
s = prs.slides.add_slide(BLANK)
content_header(s, "Tangible Yearly Cost Savings", 6)
rows = [
    ("Re-testing incl. test cost & time", "865 020", "Test institute and PE admin"),
    ("Product damages in re-test", "160 000", "Product damages in test"),
    ("Replacing packaging materials", "280 000", "New pkg materials at re-test"),
    ("Travels", "30 000", "To test institute if not in Kista"),
    ("TTM lead-time reduction", "2 680 992", "Lead time reduced by 10%"),
    ("Packaging-related claims (quality)", "1 210 000", "Reduce claims cost by 20%"),
    ("TK reduction", "3 448 620", "1% reduction. Volume value 2026"),
    ("Total", "8 674 632", ""),
]
add_table(s, Inches(0.75), Inches(1.45), Inches(11.8),
          ["Item", "Cost saving / year (SEK)", "Comments"],
          rows,
          [Inches(4.6), Inches(2.8), Inches(4.4)],
          body_size=12, header_size=12, row_h=0.58)
add_text(s, Inches(0.75), Inches(6.5), Inches(11.8), Inches(0.4),
         "Estimated annual business value \u2248 8.67 MSEK (before license cost).",
         12, ERICSSON_BLUE, bold=True)

# ========================================= SLIDE 7 - PRE-DEV ACTIVITIES (1)
s = prs.slides.add_slide(BLANK)
content_header(s, "Pre-Dev Simulation Activities 2026 (1 of 2)", 7)
rows = [
    ("1", "Calculate & verify MAT_PAPER for remaining paper qualities from DS Smith tensile "
          "testing (5 GSM qualities; MD, CD & 45\u00b0 directions)"),
    ("2", "Practice adapting the tape geometry for other boxes in Discovery"),
    ("3", "Modify & run 19-inch model with changed paper quality for the flute"),
    ("4", "Practice tensile test with new extensometer \u2013 paper, corrugated, EPP & EPE"),
    ("5", "Collect paper samples from DSS and corrugated materials from Nefab \u2013 WoW"),
    ("6", "Practice folding fiber boxes & fitments from a 2D drawing; create folding schedules"),
    ("7", "Simulation project with new Radio product(s) with fiber solution"),
    ("8", "Get DSS to deliver data table (GSM/grammage & thickness) for all new design proposals"),
    ("9", "Get or measure data for the EPP fitment used in 19-inch"),
    ("10", "Investigate simulation of molded-pulp fitments \u2013 material data, meshing setup"),
    ("11", "Change 19-inch product to a solid model (instead of rigid) and simulate"),
]
add_table(s, Inches(0.75), Inches(1.4), Inches(11.8),
          ["No", "Activity"],
          rows, [Inches(0.8), Inches(11.0)],
          body_size=10.5, header_size=11, row_h=0.45)

# ========================================= SLIDE 8 - PRE-DEV ACTIVITIES (2)
s = prs.slides.add_slide(BLANK)
content_header(s, "Pre-Dev Simulation Activities 2026 (2 of 2)", 8)
rows = [
    ("12", "Check with Nefab, DSS, IKEA etc. for experience in molded-pulp simulation"),
    ("13", "Define templates and describe in LS-Dyna"),
    ("14", "Define sequential drop and describe in LS-Dyna"),
    ("15", "Define automation and describe in LS-Dyna"),
    ("16", "Look into Python scripts in LS-Dyna"),
    ("17", "Practice using LS-PrePost for analyzing simulation results"),
    ("18", "Define guidelines for analyzing results \u2013 G-values, energies, forces, graphs, movies"),
    ("19", "Create a template for the simulation report"),
    ("20", "Define SEM (Simulation Estimation Meeting) and update HWDP \u2013 inputs & outputs"),
    ("21", "Define a library for material properties"),
    ("22", "Simulation project with new 19-inch Base Band product(s) with fiber solution"),
    ("23", "Simulation project with new product(s) with molded-pulp fiber solution"),
]
add_table(s, Inches(0.75), Inches(1.4), Inches(11.8),
          ["No", "Activity"],
          rows, [Inches(0.8), Inches(11.0)],
          body_size=10.5, header_size=11, row_h=0.42)

# ================================================= SLIDE 9 - NEXT STEPS
s = prs.slides.add_slide(BLANK)
content_header(s, "Status & Next Steps", 9)
bullets(s, Inches(0.75), Inches(1.5), Inches(11.8), Inches(5.0), [
    ("Pilot technical foundation established: Ansys + LS-Dyna, fiber material cards, "
     "6-drop template and the virtual-lab tensile method", 0),
    ("Pilot extended through year-end 2026 at ~0.1 FTE each for Andreas and Peter", 0),
    ("Continuing Packaging Simulation Pre-Dev series with PMD, EAS Sim and Ansys/Synopsys", 0),
    ("Move 19-inch product to a flexible (solid) model; develop corrugated-board geometry "
     "scripts for single- and double-wall structures", 0),
    ("Enable HPS access and tensile testing (Kenneth Wing\u00e5rdh)", 0),
    ("Correlate simulated G-values with real drop-test results before the method is trusted", 1),
    ("Target approved G-values per product weight & construction; make simulation part of "
     "PMD verification and eventually HWDP for new packaging", 0),
    ("Commercial Ansys LS-Dyna licensing approved (Dec 2025): ~8.65 MSEK annual value vs. "
     "~1.4 MSEK license cost; deploy via HPS reusing the Ansys Mech license pool", 0),
], size=14, gap=10)

# ====================================================== SLIDE 10 - CLOSING
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, SW, SH, ERICSSON_BLUE)
add_rect(s, Inches(0.9), Inches(2.6), Inches(0.18), Inches(1.6), TEAL)
add_text(s, Inches(1.25), Inches(2.7), Inches(10.8), Inches(1.5),
         "From proof-of-concept to a repeatable,\nsustainable packaging capability",
         28, WHITE, bold=True)
add_text(s, Inches(1.25), Inches(4.4), Inches(10.8), Inches(0.6),
         "Thank you", 20, RGBColor(0xBF, 0xD9, 0xF2))
add_text(s, Inches(0.9), Inches(6.9), Inches(11.5), Inches(0.4),
         f"{SECURITY}   |   {REVISION}   |   {DATE}   |   {PREPARED}",
         10, RGBColor(0x9F, 0xC2, 0xE8))

# -------------------------------------------------------------------- save
import sys
out = sys.argv[1] if len(sys.argv) > 1 else "Packaging_Simulation_Pilot_Summary.pptx"
prs.save(out)
print("Saved:", out)
print("Slides:", len(prs.slides._sldIdLst))
