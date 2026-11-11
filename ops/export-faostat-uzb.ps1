param(
    [string]$GlobalRepo = "E:\osh-agriculture-ai-global-deploy"
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$centralHome = if ($env:OSH_AGRI_CENTRAL_HOME) {
    $env:OSH_AGRI_CENTRAL_HOME
} else {
    Join-Path $env:LOCALAPPDATA "OSH\AgricultureAI-Central"
}

# Reuse the Python environment already used by the global OSH archive.
$pythonCandidates = @(
    (Join-Path $centralHome ".venv\Scripts\python.exe"),
    (Join-Path $GlobalRepo ".venv\Scripts\python.exe"),
    (Join-Path $repoRoot ".venv\Scripts\python.exe")
)
$python = $null
foreach ($candidate in $pythonCandidates) {
    if (Test-Path -LiteralPath $candidate) {
        $python = $candidate
        break
    }
}
if (-not $python) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) { $python = $pythonCommand.Source }
}
if (-not $python) {
    throw "Python topilmadi. Global OSH loyihasidagi Python muhitini tekshiring."
}

# The password is read locally from the user's PostgreSQL pgpass.conf.
# Never place DATABASE_URL credentials or passwords in this script.
$env:DATABASE_URL = "postgresql+psycopg://osh_global_app@127.0.0.1:5433/osh_agriculture_global"
$env:PYTHONUTF8 = "1"
$output = Join-Path $repoRoot "data\faostat\UZB_QCL.json"
$exporter = Join-Path $repoRoot "scripts\export_faostat_uzb.py"

Write-Host "FAOSTAT UZB eksporti: faqat SELECT, source=FAOSTAT_QCL, country=UZB."
Write-Host "Manba: 127.0.0.1:5433 / osh_agriculture_global."
Write-Host "Global ma'lumotlar bazasi o'zgartirilmaydi."
& $python $exporter --output $output
if ($LASTEXITCODE -ne 0) {
    throw "FAOSTAT eksporti muvaffaqiyatsiz tugadi (exit $LASTEXITCODE). PostgreSQL, pgpass.conf, SQLAlchemy va psycopg ni tekshiring."
}

Write-Host ""
Write-Host "EXPORT TAYYOR: $output"
Write-Host "Endi faqat ushbu JSON faylni O'zbekiston repozitoriysiga commit/push qiling."
