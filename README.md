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

**Capability Model** — 116 capabilities across 14 functional areas and 5 groups. Each
capability is sized as a single product decision and carries:

- the Microsoft first-party product and its key components
- a coverage rating — `Native`, `Partial` or `Gap`
- named non-Microsoft alternatives
- a candid positioning statement
- a link to the authoritative Microsoft Learn page
- a tier — `Essential`, `Standard` or `Advanced`

**Reference Implementation** — one real initiative expressed against the model, with an
interactive flow diagram, control planes, and a closing note on where the design depends
on custom build rather than a first-party product.

## Structure

```
docs/
  index.html    # the self-contained SPA — no build step, no external assets
  .nojekyll     # serve files as-is, skip Jekyll processing
archive/        # superseded iterations, not published (gitignored)
```

## Updating

`docs/index.html` is the single source of truth. Edit it directly and push:

```powershell
git add docs/index.html
git commit -m "Update capability model"
git push
```

Pages redeploys automatically from `main` / `/docs`.

## Design constraints

The file is deliberately **self-contained** — no CDN, no external scripts, no web fonts.
It renders from a local file, from OneDrive/SharePoint preview, and from Pages without
modification. Any change that introduces an external reference breaks that property.

Product names and coverage ratings are researched against current Microsoft
documentation rather than recalled, and gaps are stated honestly — the value of the
model rests on it being trustworthy where it says Microsoft does not cover something.
