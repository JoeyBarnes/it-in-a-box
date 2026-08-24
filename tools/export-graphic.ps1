# Export the overview graphic from the page itself.
#
# The page generates the graphic from AREAS/MAP at runtime (overviewSVG() in
# docs/index.html), so this script does not hold a second copy of the model —
# it drives the real generator and saves the result. That is the whole point:
# there is exactly one definition of the graphic, and it is the one users get
# from the Download buttons.
#
#   pwsh tools\export-graphic.ps1
#
# Writes docs/it-in-a-box-overview.svg and docs/it-in-a-box-overview.png.

[CmdletBinding()]
param(
    [ValidateSet('light', 'dark')]
    [string]$Theme = 'light',
    [int]$Scale = 2
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$docs = Join-Path $root 'docs'
$index = Join-Path $docs 'index.html'
if (-not (Test-Path $index)) { throw "not found: $index" }

$edge = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
if (-not (Test-Path $edge)) { $edge = 'C:\Program Files\Microsoft\Edge\Application\msedge.exe' }
if (-not (Test-Path $edge)) { throw 'Microsoft Edge not found' }

# Edge writes progress to stderr. Under ErrorActionPreference='Stop' PowerShell
# turns that into a terminating NativeCommandError even on a successful run, so
# native calls are isolated here and stderr is dropped.
function Invoke-Edge {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$EdgeArgs)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $edge @EdgeArgs 2>&1 |
            Where-Object { $_ -isnot [System.Management.Automation.ErrorRecord] }
    }
    finally { $ErrorActionPreference = $prev }
}

$html = Get-Content $index -Raw
if ($Theme -eq 'dark') {
    $html = $html.Replace('localStorage.getItem("ptom-theme")||"light"', '"dark"')
}

# Replace the document with just the generated SVG so it can be lifted out of
# the dumped DOM cleanly.
$probe = @'
<script>
setTimeout(function(){
  try{ document.documentElement.innerHTML="<head></head><body>"+overviewSVG()+"</body>"; }
  catch(e){ document.documentElement.innerHTML="<head></head><body>GENFAIL "+e.message+"</body>"; }
},400);
</script>
</body>
'@

$tmp = Join-Path $docs '_export_tmp.html'
($html -replace '</body>', $probe) | Set-Content -Encoding UTF8 $tmp

try {
    $uri = ([System.Uri]$tmp).AbsoluteUri
    $dom = Invoke-Edge --headless=new --disable-gpu --no-first-run --no-default-browser-check `
        --virtual-time-budget=8000 --dump-dom $uri | Out-String

    if ($dom -match 'GENFAIL (.+)') { throw "generator failed: $($Matches[1])" }

    $m = [regex]::Match($dom, '(?s)<svg .*?</svg>')
    if (-not $m.Success) { throw 'no <svg> found in the rendered DOM' }

    $svg = '<?xml version="1.0" encoding="UTF-8"?>' + "`n" + $m.Value
    $svgPath = Join-Path $docs 'it-in-a-box-overview.svg'
    [System.IO.File]::WriteAllText($svgPath, $svg, (New-Object System.Text.UTF8Encoding $false))

    $dim = [regex]::Match($svg, 'width="(\d+)" height="(\d+)"')
    $w = [int]$dim.Groups[1].Value
    $h = [int]$dim.Groups[2].Value

    $pngPath = Join-Path $docs 'it-in-a-box-overview.png'
    Remove-Item $pngPath -ErrorAction SilentlyContinue
    Invoke-Edge --headless=new --disable-gpu --hide-scrollbars --no-first-run --no-default-browser-check `
        --force-device-scale-factor=$Scale --virtual-time-budget=4000 `
        --screenshot="$pngPath" --window-size="$w,$h" ([System.Uri]$svgPath).AbsoluteUri | Out-Null

    Start-Sleep -Seconds 2
    if (-not (Test-Path $pngPath)) { throw 'PNG rasterisation produced no file' }

    $caps = ([regex]::Matches($html, '\{id:"\d\d\.\d+",name:')).Count
    $areas = ([regex]::Matches($html, '\{id:"\d\d",g:"G\d"')).Count
    "svg  {0,6:N0} bytes  {1}x{2}" -f (Get-Item $svgPath).Length, $w, $h
    "png  {0,6:N0} bytes  {1}x{2}" -f (Get-Item $pngPath).Length, ($w * $Scale), ($h * $Scale)
    "from $areas areas / $caps capabilities in the model, theme=$Theme"
}
finally {
    Remove-Item $tmp -ErrorAction SilentlyContinue
}
