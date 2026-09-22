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

**Capability Model** — 141 capabilities across 15 functional areas and 6 groups. Each
capability is sized as a single product decision and carries:

- the Microsoft first-party product and its key components
- a coverage rating — `Native`, `Partial` or `Gap`
- named non-Microsoft alternatives
- a candid positioning statement
- a link to the authoritative Microsoft Learn page
- a tier — `Essential`, `Standard` or `Advanced`

Capabilities that are a management discipline rather than a product purchase are marked
`Practice`, so a `Gap` rating is not misread as a missing product.

**Fit** — where a business sits against the documented limits in the Microsoft stack. Eleven
published limits, each linked to its source, running high-level to detail: scale and requirements,
then a coverage summary, then product constraints, then the findings in full, then the open
decisions.

The page reports what a limit **rules out** and stops there. Crossing 300 seats removes Defender
for Business; it does not establish what should replace it.

Evidence is separated by strength rather than lumped together. A **hard boundary** removes an
option outright. A **design constraint** is real and documented but has known mitigations — the
SharePoint 5,000-item figure governs a view, not a corpus, and a list can hold 30 million items,
so it shapes how views are built rather than ruling SharePoint out. **Vendor guidance** is
Microsoft's own advice whose assumptions are unpublished, so the PPU break-even prompts you to
model your own numbers rather than deciding anything.

A check runs only when the figures it needs are supplied, and separately only when the rule is
known to **apply**. A list past 100,000 items says nothing until you know whether the design
breaks permission inheritance — without that the answer is "applicability not established",
which is neither crossed nor clear.

**Product constraints** answers the original brief's question about products by scale, as far as
evidence honestly reaches: what the entered figures rule out, product by product. A product is
never marked *eligible* — eleven checks passing establishes only that these boundaries were not
crossed. Nothing is ranked.

**Scale bands** are Microsoft's own two published seat thresholds — 300 (the Business family cap)
and 2,500 (the Lighthouse ceiling) — so even the band edges are not invented. A band sets a seat
count and nothing else, because seats is the only figure company size actually determines.
Directory objects, list sizes and capacity SKUs are architecture and workload choices that do not
follow from headcount. **Requirements** are separate toggles on a separate axis, each setting
exactly the one field it names, because regulation is not a size.

The view also lists **where Microsoft publishes no threshold** — size bands above 300 seats,
Fabric capacity by organisation size, the Power Apps per-app break-even, Teams Phone seat caps, a
subscription count forcing a split, and landing zones by size. Stating these is the point: it is
where a number would otherwise get invented.

**Reference Implementation** — one real initiative expressed against the model, with an
interactive flow diagram, control planes, and a closing note on where the design depends
on custom build rather than a first-party product.

**Product Map** — the model read backwards: every Microsoft product it names, drawn as a
bubble sized by how many capabilities it answers, with a grid view for reading names and
areas. Clicking a product lists its capabilities and jumps into the model.

Workloads that Microsoft positions as part of a bigger platform are rolled into the parent,
so Purview counts once rather than five times and Power BI sits inside Fabric. The roll-up
takes 124 named products down to 100.

That grouping follows **how Microsoft architects these products, not how they are billed**.
The two diverge often enough that conflating them would mislead — Power BI is a Fabric
workload in Microsoft's architecture yet Power BI Pro is its own per-user licence, and
Codespaces is metered apart from GitHub Enterprise seats. Licensing therefore stays attached
at capability level and is reported as a spread on each product, so a large circle means one
platform rather than one purchase order.

Peer products in a family stay separate even where the brand is shared. The Entra product
family lists ID Governance, ID Protection and Verified ID *alongside* Entra ID rather than
inside it, so they are separate here and PIM sits under ID Governance. Defender for Endpoint
and Defender for Office 365 are products whose signals Defender XDR coordinates, so folding
them into XDR would double-count them.

The picture that falls out is the point: **19 products cover more than one capability, 71
cover exactly one**, and 10 only ever contribute to a capability someone else answers. The
big circles are where one platform is already earning its keep across the estate.

Two properties of the underlying data are handled explicitly rather than inferred. `ms` in
`MAP` is a display label, not a product identity — it compounds two products in 19 places
and fragments families across separate labels. So the edges live in `CAP_PROD`, curated per
capability, and each carries a role, because a module library that extends a product is not
a co-equal answer to the capability. `checkProducts()` validates the edges and the roll-up
against `MAP` at load and logs loudly if they drift.

**Overview graphic** — the Overview tab has **Download SVG** and **Download PNG** buttons. The
graphic is generated in the browser from the model itself at click time, in whichever theme is
active, so a download always matches what is on screen and can never drift from the data. Text
is laid out using real canvas metrics rather than estimated widths, so cells are sized to their
actual content.

A snapshot of that same output is committed for direct linking:

| File | Use |
| --- | --- |
| `docs/it-in-a-box-overview.svg` | vector — documents, print, scaling |
| `docs/it-in-a-box-overview.png` | 3440×2000 raster — Teams, PowerPoint, chat |

## Structure

```
docs/
  index.html                  # the self-contained SPA — no build step, no external assets
  it-in-a-box-overview.svg    # snapshot of the in-page graphic (generated)
  it-in-a-box-overview.png    # 2x raster of the same (generated)
  .nojekyll                   # serve files as-is, skip Jekyll processing
tools/
  export-graphic.ps1          # drives the page's own generator to refresh the two snapshots
presentation/
  build-journey.html          # how the model was built and why — tracked, not published
archive/                      # superseded iterations, not published (gitignored)
```

The presentation is a companion piece rather than a superseded one, which is why
it is tracked rather than left in `archive/`. It is deliberately **not** in `docs/`,
so it is versioned with the model without being served from the public site. It is
self-contained in the same way `index.html` is — open it directly in a browser.

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
