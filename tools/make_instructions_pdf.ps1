# Renders tools/instructions.html to "Website instructions.pdf" (repo root) with Microsoft Edge.
# Usage (PowerShell, from the repo root):  & .\tools\make_instructions_pdf.ps1

$root = Split-Path -Parent $PSScriptRoot
$html = Join-Path $PSScriptRoot "instructions.html"
$pdf = Join-Path $root "Website instructions.pdf"
$edge = "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
if (-not (Test-Path $edge)) { $edge = "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe" }

$url = "file:///" + ($html -replace '\\', '/')
& $edge --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=8000 "--print-to-pdf=$pdf" $url | Out-Null
Write-Output "wrote $pdf"
