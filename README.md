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

**Capability Model** — 120 capabilities across 14 functional areas and 5 groups. Each
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

**Overview graphic** — a one-page stack view of all 14 areas for decks, documents and
Teams. Security spans the stack as the left rail, governance and business management as
the right rail, business-facing areas across the top, and the platform and operating
layers descending beneath them.

| File | Use |
| --- | --- |
| `docs/it-in-a-box-stack.svg` | vector — documents, print, scaling |
| `docs/it-in-a-box-stack.png` | 3440×1840 raster — Teams, PowerPoint, chat |

## Structure

```
docs/
  index.html               # the self-contained SPA — no build step, no external assets
  it-in-a-box-stack.svg    # one-page overview graphic (generated)
  it-in-a-box-stack.png    # 2x raster of the same (generated)
  .nojekyll                # serve files as-is, skip Jekyll processing
tools/
  make_stack_svg.py        # regenerates the overview graphic
archive/                   # superseded iterations, not published (gitignored)
```

## Updating

`docs/index.html` is the single source of truth. Edit it directly and push:

```powershell
git add docs/index.html
git commit -m "Update capability model"
git push
```

Pages redeploys automatically from `main` / `/docs`.

### Regenerating the overview graphic

The graphic carries its own copy of the area names and counts, so it must be updated
when the model changes. The generator asserts 14 areas and 120 capabilities and reports
any rail text that would overflow its cell, so a drift will fail loudly rather than
render wrong.

```powershell
python tools\make_stack_svg.py

# re-render the raster from the SVG
$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
& $edge --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 `
        --screenshot="docs\it-in-a-box-stack.png" --window-size=1720,920 `
        ([System.Uri]"$PWD\docs\it-in-a-box-stack.svg").AbsoluteUri
```

## Design constraints

The file is deliberately **self-contained** — no CDN, no external scripts, no web fonts.
It renders from a local file, from OneDrive/SharePoint preview, and from Pages without
modification. Any change that introduces an external reference breaks that property.

Product names and coverage ratings are researched against current Microsoft
documentation rather than recalled, and gaps are stated honestly — the value of the
model rests on it being trustworthy where it says Microsoft does not cover something.
