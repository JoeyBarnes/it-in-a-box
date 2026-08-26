# IT-in-a-Box

A complete model of an enterprise technology function — every capability a business
needs in order to operate, expressed as a reusable standard rather than as any one
company's organisation chart.

Published as a self-contained single-page site via GitHub Pages.

## Live site

```
https://joeybarnes.github.io/it-in-a-box/
```

## What it contains

**Overview** — the whole stack on one page. Cyber security spans the full height as the left
rail, governance and business management as the right rail, the four business-facing areas
across the top, and the data, platform and operating layers descending beneath them. Each area
shows its name, size, Microsoft coverage mix and one-line definition — the capability names
themselves stay in the Capability Model, so this reads as an orientation view rather than a
second copy of the model. Every label, count and coverage bar is read from the model at build
time, so the view cannot drift from the data behind it. Selecting an area opens it there.

**Capability Model** — 140 capabilities across 15 functional areas and 6 groups. Each
capability is sized as a single product decision and carries:

- the Microsoft first-party product and its key components
- a coverage rating — `Native`, `Partial` or `Gap`
- named non-Microsoft alternatives
- a candid positioning statement
- a link to the authoritative Microsoft Learn page
- a tier — `Essential`, `Standard` or `Advanced`

Capabilities that are a management discipline rather than a product purchase are marked
`Practice`, so a `Gap` rating is not misread as a missing product.

**Reference Implementation** — one real initiative expressed against the model, with an
interactive flow diagram, control planes, and a closing note on where the design depends
on custom build rather than a first-party product.

**Overview graphic** — the Overview tab has **Download SVG** and **Download PNG** buttons. The
graphic is generated in the browser from the model itself at click time, in whichever theme is
active, so a download always matches what is on screen and can never drift from the data. Text
is laid out using real canvas metrics rather than estimated widths, so cells are sized to their
actual content.

A snapshot of that same output is committed for direct linking:

| File | Use |
| --- | --- |
| `docs/it-in-a-box-overview.svg` | vector — documents, print, scaling |
| `docs/it-in-a-box-overview.png` | 3440×2316 raster — Teams, PowerPoint, chat |

## Structure

```
docs/
  index.html                  # the self-contained SPA — no build step, no external assets
  it-in-a-box-overview.svg    # snapshot of the in-page graphic (generated)
  it-in-a-box-overview.png    # 2x raster of the same (generated)
  .nojekyll                   # serve files as-is, skip Jekyll processing
tools/
  export-graphic.ps1          # drives the page's own generator to refresh the two snapshots
archive/                      # superseded iterations, not published (gitignored)
```

## Updating

`docs/index.html` is the single source of truth. Edit it directly and push:

```powershell
git add docs/index.html
git commit -m "Update capability model"
git push
```

Pages redeploys automatically from `main` / `/docs`.

### Refreshing the committed graphic

The graphic has no separate definition — `overviewSVG()` in `docs/index.html` builds it from
`AREAS`/`MAP`. The export script drives that function in headless Edge and saves the result, so
there is no second copy of the model to keep in step:

```powershell
pwsh tools\export-graphic.ps1            # light theme, 2x PNG
pwsh tools\export-graphic.ps1 -Theme dark
```

## Design constraints

The file is deliberately **self-contained** — no CDN, no external scripts, no web fonts.
It renders from a local file, from OneDrive/SharePoint preview, and from Pages without
modification. Any change that introduces an external reference breaks that property.

Product names and coverage ratings are researched against current Microsoft
documentation rather than recalled, and gaps are stated honestly — the value of the
model rests on it being trustworthy where it says Microsoft does not cover something.

## What belongs in the model

A capability earns its place if it is **a distinct estate category that an assessment
must cover, and it is sized as one product-selection decision**. That is the operative
test, and it is why the model carries capabilities Microsoft has no answer for at all —
control systems, service desk, software asset management, EHS, physical security.

A weaker test is sometimes reached for — *"a gap is only worth listing if a reader might
assume Microsoft covers it"* — but that one does not describe the model. Nobody assumes
Microsoft sells SCADA, and `07.11` is in here. It is useful only as a tiebreaker for
genuinely borderline cases, and it is the reason LAN and Wi-Fi switching is deliberately
absent.

Area 15 Operational & Engineering Systems is scoped by one rule: a capability belongs
there if it exists **because the business owns physical things** rather than only
information. Capabilities whose subject is operational but whose function is not —
OT network segregation, the operational historian, industrial connectivity, OT security
— deliberately stay in the network, data, integration and security areas, because the
model is organised by function rather than by domain.

Things that fail the test and are excluded by design: treasury, tax, travel and expense,
learning management and investor reporting. Each is a module of something already in the
model — ERP, HCM or BI — rather than a separate estate. Breaking them out would turn
area 07 into an application catalogue, which is what the compression is there to prevent.
