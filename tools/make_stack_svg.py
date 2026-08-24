"""Generate the IT-in-a-Box one-page stack graphic as a self-contained SVG.

Mirrors the capability model in docs/index.html: 120 capabilities, 14 functional
areas, 5 groups. Colours are the light-mode values of the Fluent 2 accent ramp
used by the page, so the graphic and the site agree.

Usage:  python tools/make_stack_svg.py
Output: docs/it-in-a-box-stack.svg
"""
import html
import pathlib

# Fluent 2 accent ramp — light-mode values from PAL in docs/index.html
CY, TE, GR, LI = "#007b84", "#0f6f68", "#0e7a0b", "#4f6f1f"
GO, AM, PI, RU = "#8a6100", "#835b00", "#a3376a", "#8c3a12"
VI, IN, CR, SL = "#6b3fa0", "#3b47c9", "#c50f1f", "#616161"

INK, INK2, INK3 = "#1b1b1f", "#424248", "#616161"
LINE, PAPER, WELL = "#d1d1d1", "#ffffff", "#fafafa"

# ---- model ---------------------------------------------------------------
# (id, name lines, colour, capability count, bullet lines)
COLUMNS = [
    ("09", ["Productivity &", "Collaboration"], VI, 8,
     ["Email, calendaring, chat", "Meetings, voice, content",
      "Intranet, search, records", "Frontline & shift comms"]),
    ("07", ["Business", "Applications"], PI, 7,
     ["Finance & ERP", "HCM & payroll",
      "Procurement & supply chain", "CRM, field service, EAM"]),
    ("08", ["Software Engineering", "& Product Technology"], RU, 7,
     ["Source control, CI/CD", "Developer tooling & test",
      "Application & product security", "Telemetry, SaaS operations"]),
    ("10", ["AI &", "Agents"], IN, 9,
     ["Copilots & assistants", "Agent platform & orchestration",
      "Grounding, models, MLOps", "Governance, safety, agent fleet"]),
]

# Each band is a list of one or two boxes: (id, name, colour, count, subtext)
BANDS = [
    [("05", "Data & Analytics", GO, 9,
      "Lakehouse · pipelines · master data · governance & catalogue · quality & lineage · BI · data science · streaming"),
     ("06", "Integration & Automation", AM, 8,
      "API management · application & data integration · events · process & robotic automation · low-code · B2B")],
    [("01", "Identity & Access Management", CY, 9,
      "Directory & lifecycle · authentication & SSO · entitlements · privileged access · governance · external, customer, workload & agent identity · identity threat detection")],
    [("02", "Endpoint & Device Management", TE, 9,
      "Provisioning · configuration · patching · app delivery · mobile & BYOD · frontline & shared · virtual desktop · analytics · disposal"),
     ("03", "Network & Connectivity", GR, 8,
      "WAN & SD-WAN · application delivery · remote access · secure internet edge · segmentation · DNS & IPAM · interconnect · assurance")],
    [("04", "Cloud Platform & Infrastructure", LI, 10,
      "Landing zones · compute & containers · storage · database · infrastructure & policy as code · backup & continuity · observability · edge · sovereignty")],
    [("13", "IT Service Management & Operations", SL, 9,
      "Service desk · incident & problem · change & release · configuration & asset · monitoring · service levels · knowledge · capacity & availability")],
]

RAIL_L = ("11", "Cyber Security", CR, 10,
          "Security operations · detection & response · exposure · data protection "
          "· cloud & workload posture · incident response")
RAIL_R = [
    ("12", ["Governance, Risk", "& Compliance"], RU, 8,
     "Policy · risk · compliance · privacy · audit"),
    ("14", ["Technology Business", "Management"], TE, 9,
     "IT finance · cloud cost · licensing · vendor · sourcing"),
]

GROUP_LEGEND = [
    ("Core Platform", CY, "01 · 02 · 03 · 04"),
    ("Data, Integration & Applications", GO, "05 · 06 · 07 · 08"),
    ("Workplace & AI", VI, "09 · 10"),
    ("Security & Governance", CR, "11 · 12"),
    ("Service & Business Management", SL, "13 · 14"),
]

# ---- geometry ------------------------------------------------------------
W = 1720
M = 30
RAIL = 104
GAP = 12
MAIN_X = M + RAIL + GAP
MAIN_W = W - 2 * M - 2 * RAIL - 2 * GAP

HEAD_H = 104
COL_H = 214
BAND_HS = [84, 84, 84, 84, 84]
FOOT_H = 92

STACK_H = COL_H + GAP + sum(h + GAP for h in BAND_HS) - GAP
# Split the right rail on a real band boundary (bottom of the 05/06 band) so the
# rail seam lines up with the stack rather than floating at an arbitrary midpoint.
RAIL_SPLIT = COL_H + GAP + BAND_HS[0]
H = HEAD_H + STACK_H + FOOT_H + M

E = html.escape
OVERFLOW = []


def wrap(text, max_chars):
    """Greedy wrap on spaces."""
    out, line = [], ""
    for tok in text.split(" "):
        cand = tok if not line else line + " " + tok
        if len(cand) > max_chars and line:
            out.append(line)
            line = tok
        else:
            line = cand
    if line:
        out.append(line)
    return out


def box(x, y, w, h, colour, side="left", sw=6, r=7):
    """Card with a rounded colour spine down the left or right edge."""
    if side == "left":
        spine = (f'M{x + sw} {y} H{x + r} A{r} {r} 0 0 0 {x} {y + r} '
                 f'V{y + h - r} A{r} {r} 0 0 0 {x + r} {y + h} H{x + sw} Z')
    else:
        xe = x + w
        spine = (f'M{xe - sw} {y} H{xe - r} A{r} {r} 0 0 1 {xe} {y + r} '
                 f'V{y + h - r} A{r} {r} 0 0 1 {xe - r} {y + h} H{xe - sw} Z')
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
        f'fill="{PAPER}" stroke="{LINE}" stroke-width="1"/>'
        f'<path d="{spine}" fill="{colour}"/>'
    )


def vblock(cx, cy, lines, span=None, label=""):
    """Vertical (bottom-to-top) centred text block.

    lines: list of (text, font-size, weight, fill, mono, offset). Each line sits
    in its own perpendicular column, so long lines can never collide with each
    other. `span` is the available rail length; overflow is reported, not hidden.
    """
    out = []
    for text, fs, wt, fill, mono, off in lines:
        if span:
            est = len(text) * fs * (0.55 if mono else (0.55 if wt >= 700 else 0.50))
            if est > span - 16:
                OVERFLOW.append(f"{label}: {est:.0f}px of {span:.0f}px — {text[:44]}...")
        fam = ' font-family="Consolas,monospace"' if mono else ""
        out.append(
            f'<g transform="translate({cx + off},{cy}) rotate(-90)">'
            f'<text text-anchor="middle" font-size="{fs}" font-weight="{wt}"'
            f'{fam} fill="{fill}">{E(text)}</text></g>')
    return "".join(out)


def chip(x, y, ident, colour):
    return (
        f'<rect x="{x}" y="{y}" width="27" height="17" rx="4" fill="{colour}" '
        f'fill-opacity="0.12" stroke="{colour}" stroke-opacity="0.35"/>'
        f'<text x="{x + 13.5}" y="{y + 12.4}" text-anchor="middle" font-size="10.5" '
        f'font-family="Consolas,monospace" font-weight="600" fill="{colour}">{ident}</text>'
    )


def count_pill(xr, y, n, colour):
    return (
        f'<text x="{xr}" y="{y}" text-anchor="end" font-size="10.5" '
        f'font-family="Consolas,monospace" fill="{colour}" fill-opacity="0.85">'
        f'{n} capabilities</text>'
    )


s = []
a = s.append

a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
  f'viewBox="0 0 {W} {H}" font-family="Segoe UI Variable Display,Segoe UI,system-ui,sans-serif">')
a(f'<rect width="{W}" height="{H}" fill="{WELL}"/>')

# ---- header --------------------------------------------------------------
a(f'<text x="{M}" y="46" font-size="30" font-weight="700" fill="{INK}">IT-in-a-Box</text>')
a(f'<text x="{M}" y="70" font-size="14" fill="{INK2}">'
  f'Enterprise technology capability model &#8212; what a complete IT estate has to answer for</text>')
a(f'<text x="{M}" y="90" font-size="12" font-family="Consolas,monospace" fill="{INK3}">'
  f'120 capabilities &#183; 14 functional areas &#183; 5 groups</text>')
a(f'<text x="{W - M}" y="46" text-anchor="end" font-size="12" '
  f'font-family="Consolas,monospace" fill="{INK3}">joeybarnes.github.io/it-in-a-box</text>')

y_top = HEAD_H

# ---- left rail -----------------------------------------------------------
rid, rname, rcol, rcount, rsub = RAIL_L
a(box(M, y_top, RAIL, STACK_H, rcol, side="left"))
a(vblock(M + RAIL / 2, y_top + STACK_H / 2, [
    (rname, 18, 700, rcol, False, 22),
    (rsub, 10.8, 400, INK3, False, 1),
    (f"{rid} · {rcount} capabilities", 10.5, 400, rcol, True, -21),
], span=STACK_H, label="rail 11"))

# ---- right rail (two stacked cells, split on a band boundary) ------------
rx = W - M - RAIL
splits = [(y_top, RAIL_SPLIT), (y_top + RAIL_SPLIT + GAP, STACK_H - RAIL_SPLIT - GAP)]
for (gid, glines, gcol, gn, gsub), (byy, bh) in zip(RAIL_R, splits):
    a(box(rx, byy, RAIL, bh, gcol, side="right"))
    rows = [(ln, 15, 700, INK, False, 22 - j * 19) for j, ln in enumerate(glines)]
    rows.append((gsub, 10.8, 400, INK3, False, -13))
    rows.append((f"{gid} · {gn} capabilities", 10.5, 400, gcol, True, -32))
    a(vblock(rx + RAIL / 2, byy + bh / 2, rows, span=bh, label=f"rail {gid}"))

# ---- top columns ---------------------------------------------------------
cw = (MAIN_W - 3 * GAP) / 4
for i, (cid, namelines, col, n, bullets) in enumerate(COLUMNS):
    x = MAIN_X + i * (cw + GAP)
    a(box(x, y_top, cw, COL_H, col))
    tx = x + 18
    a(chip(tx, y_top + 16, cid, col))
    ty = y_top + 55
    for ln in namelines:
        a(f'<text x="{tx}" y="{ty}" font-size="16" font-weight="700" fill="{INK}">{E(ln)}</text>')
        ty += 20
    yy = ty + 14
    for b in bullets:
        a(f'<circle cx="{tx + 3}" cy="{yy - 4}" r="2.1" fill="{col}"/>')
        a(f'<text x="{tx + 13}" y="{yy}" font-size="11.8" fill="{INK2}">{E(b)}</text>')
        yy += 19
    a(count_pill(x + cw - 16, y_top + COL_H - 14, n, col))

# ---- bands ---------------------------------------------------------------
yb = y_top + COL_H + GAP
for band, bh in zip(BANDS, BAND_HS):
    widths = [MAIN_W] if len(band) == 1 else [(MAIN_W - GAP) / 2] * 2
    bx = MAIN_X
    for (bid, bname, bcol, bn, sub), bwid in zip(band, widths):
        a(box(bx, yb, bwid, bh, bcol))
        tx = bx + 18
        a(chip(tx, yb + 14, bid, bcol))
        a(f'<text x="{tx + 36}" y="{yb + 27}" font-size="16" font-weight="700" '
          f'fill="{INK}">{E(bname)}</text>')
        a(count_pill(bx + bwid - 16, yb + 27, bn, bcol))
        maxc = int((bwid - 36) / 5.85)
        sy = yb + 50
        for ln in wrap(sub, maxc)[:2]:
            a(f'<text x="{tx}" y="{sy}" font-size="11.6" fill="{INK2}">{E(ln)}</text>')
            sy += 17
        bx += bwid + GAP
    yb += bh + GAP

# ---- footer legend -------------------------------------------------------
fy = y_top + STACK_H + 36
a(f'<line x1="{M}" y1="{fy - 21}" x2="{W - M}" y2="{fy - 21}" stroke="{LINE}"/>')
a(f'<text x="{M}" y="{fy}" font-size="11" font-family="Consolas,monospace" '
  f'fill="{INK3}">GROUPS</text>')
lx = M + 76
for gname, gcol, ids in GROUP_LEGEND:
    a(f'<rect x="{lx}" y="{fy - 9}" width="10" height="10" rx="2.5" fill="{gcol}"/>')
    a(f'<text x="{lx + 16}" y="{fy}" font-size="12" font-weight="600" fill="{INK2}">{E(gname)}</text>')
    a(f'<text x="{lx + 16}" y="{fy + 16}" font-size="10.5" font-family="Consolas,monospace" '
      f'fill="{INK3}">{E(ids)}</text>')
    lx += 30 + len(gname) * 6.9

a(f'<text x="{M}" y="{fy + 46}" font-size="10.5" fill="{INK3}">'
  f'Each capability is sized as a single product-selection decision and mapped to its Microsoft '
  f'first-party answer with a coverage rating, named alternatives and a Microsoft Learn reference. '
  f'Created with the assistance of Microsoft Scout, which uses AI &#8212; verify anything you intend '
  f'to rely on for a decision.</text>')

a('</svg>')

out = pathlib.Path(__file__).resolve().parent.parent / "docs" / "it-in-a-box-stack.svg"
out.write_text("\n".join(s), encoding="utf-8")
print(f"wrote {out}  ({out.stat().st_size:,} bytes)  {W}x{H}")

total = sum(c[3] for c in COLUMNS) + sum(b[3] for band in BANDS for b in band) \
    + RAIL_L[3] + sum(g[3] for g in RAIL_R)
areas = len(COLUMNS) + sum(len(b) for b in BANDS) + 1 + len(RAIL_R)
print(f"areas={areas} (expect 14)   capabilities={total} (expect 120)")
assert areas == 14 and total == 120, "graphic is out of sync with the model"

if OVERFLOW:
    print("OVERFLOW:")
    for o in OVERFLOW:
        print("  " + o)
else:
    print("no rail text overflow")
