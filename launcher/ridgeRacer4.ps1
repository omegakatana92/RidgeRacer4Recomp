# Ridge Racer 4 Launcher
# A lightweight Windows GUI that locates the recompiled executable next to
# itself, asks the user to pick a legally obtained .cue file and (optionally)
# a custom legally obtained PS1 BIOS, and launches the game with the runtime
# flags it actually supports.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\launcher\ridgeRacer4.ps1
# Or use the provided .bat wrapper.
#
# Design notes:
#   * No external dependencies (uses only built-in System.Windows.Forms).
#   * The recompiled EXE is resolved relative to the script's location so the
#     release folder can be moved to any Windows PC.
#   * Configuration (last CUE, BIOS mode, custom BIOS path) is persisted in
#     %APPDATA%\RidgeRacer4Recomp\launcher-config.json (per-user). Falls back
#     to launcher-config.json next to the launcher if %APPDATA% is unavailable.
#   * Never bundles or copies a game disc image or retail BIOS.
#   * OpenBIOS is loaded from bios\openbios.bin when present. Older release
#     archives may omit it; report that explicitly instead of claiming inclusion.
#   * The launched process uses the directory containing the selected CUE
#     as its WorkingDirectory, because multi-track CUE files reference the
#     track .bin files with relative FILE entries. Using the build directory
#     as the working directory will fail to find the tracks.

[CmdletBinding()]
param(
    [string]$RecompExeName = 'Ridge_Racer_4_Recompiled.exe'
)

$ErrorActionPreference = 'Stop'

# Load Windows Forms (built into Windows PowerShell 5.1 / .NET Framework).
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# --- Locate the recompiled EXE and the bundled OpenBIOS relative to this script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
# launcher/ lives inside the release root. The EXE and bios/ are its siblings.
$gameDir = Split-Path -Parent $scriptDir
$recompExePath = Join-Path $gameDir $RecompExeName
$bundledBiosPath = Join-Path (Join-Path $gameDir 'bios') 'openbios.bin'

# --- Config persistence -------------------------------------------------------
function Get-ConfigDir {
    $appData = [Environment]::GetFolderPath('ApplicationData')
    if ([string]::IsNullOrWhiteSpace($appData)) {
        return $scriptDir
    }
    $dir = Join-Path $appData 'RidgeRacer4Recomp'
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    return $dir
}

function Get-ConfigPath {
    Join-Path (Get-ConfigDir) 'launcher-config.json'
}

function Read-Config {
    $path = Get-ConfigPath
    if (Test-Path $path) {
        try {
            $raw = Get-Content -Path $path -Raw -Encoding UTF8
            if ([string]::IsNullOrWhiteSpace($raw)) { return $null }
            return $raw | ConvertFrom-Json
        } catch {
            return $null
        }
    }
    return $null
}

function Write-Config {
    param(
        [string]$DiscPath,
        [string]$BiosMode,         # 'openbios' or 'custom'
        [string]$CustomBiosPath
    )
    $cfg = [pscustomobject]@{
        disc_path        = $DiscPath
        bios_mode        = $BiosMode
        custom_bios_path = $CustomBiosPath
        saved_utc        = (Get-Date).ToUniversalTime().ToString('o')
    }
    $json = $cfg | ConvertTo-Json -Depth 3
    Set-Content -Path (Get-ConfigPath) -Value $json -Encoding UTF8
}

# --- Build the UI -------------------------------------------------------------
$form = New-Object System.Windows.Forms.Form
$form.Text = 'Ridge Racer 4 Launcher'
$form.Size = New-Object System.Drawing.Size(760, 360)
$form.MinimumSize = New-Object System.Drawing.Size(620, 360)
$form.StartPosition = 'CenterScreen'
$form.FormBorderStyle = 'FixedDialog'
$form.MaximizeBox = $false

# Top info label
$lblInfo = New-Object System.Windows.Forms.Label
$lblInfo.Text = "Select your legally obtained Ridge Racer Type 4 disc image (.cue).
Choose OpenBIOS (if installed) or your own legally obtained PS1 BIOS. Click Launch Game to start."
$lblInfo.Location = New-Object System.Drawing.Point(16, 12)
$lblInfo.Size = New-Object System.Drawing.Size(720, 40)
$lblInfo.AutoSize = $false
$form.Controls.Add($lblInfo)

# --- BIOS group box -----------------------------------------------------------
$grpBios = New-Object System.Windows.Forms.GroupBox
$grpBios.Text = 'BIOS'
$grpBios.Location = New-Object System.Drawing.Point(16, 60)
$grpBios.Size = New-Object System.Drawing.Size(720, 90)
$form.Controls.Add($grpBios)

$rbOpenBIOS = New-Object System.Windows.Forms.RadioButton
$openBiosAvailable = Test-Path -LiteralPath $bundledBiosPath -PathType Leaf
$rbOpenBIOS.Text = $(if ($openBiosAvailable) { 'OpenBIOS (available)' } else { 'OpenBIOS (missing - see README)' })
$rbOpenBIOS.Location = New-Object System.Drawing.Point(16, 24)
$rbOpenBIOS.AutoSize = $true
$rbOpenBIOS.Checked = $true
$grpBios.Controls.Add($rbOpenBIOS)

$rbCustom = New-Object System.Windows.Forms.RadioButton
$rbCustom.Text = 'Custom BIOS'
$rbCustom.Location = New-Object System.Drawing.Point(16, 56)
$rbCustom.AutoSize = $true
$grpBios.Controls.Add($rbCustom)

$txtCustomBios = New-Object System.Windows.Forms.TextBox
$txtCustomBios.Location = New-Object System.Drawing.Point(160, 54)
$txtCustomBios.Size = New-Object System.Drawing.Size(440, 24)
$txtCustomBios.Enabled = $false
$grpBios.Controls.Add($txtCustomBios)

$btnBrowseBios = New-Object System.Windows.Forms.Button
$btnBrowseBios.Text = 'Browse...'
$btnBrowseBios.Location = New-Object System.Drawing.Point(608, 53)
$btnBrowseBios.Size = New-Object System.Drawing.Size(96, 26)
$btnBrowseBios.Enabled = $false
$grpBios.Controls.Add($btnBrowseBios)

# Enable/disable custom BIOS controls when the radio changes
$rbCustom.Add_CheckedChanged({
    $enabled = $rbCustom.Checked
    $txtCustomBios.Enabled = $enabled
    $btnBrowseBios.Enabled = $enabled
})
$rbOpenBIOS.Add_CheckedChanged({
    if ($rbOpenBIOS.Checked) {
        $txtCustomBios.Enabled = $false
        $btnBrowseBios.Enabled = $false
    }
})

# --- Disc CUE group -----------------------------------------------------------
$lblDisc = New-Object System.Windows.Forms.Label
$lblDisc.Text = 'Disc CUE:'
$lblDisc.Location = New-Object System.Drawing.Point(16, 162)
$lblDisc.AutoSize = $true
$form.Controls.Add($lblDisc)

$txtDisc = New-Object System.Windows.Forms.TextBox
$txtDisc.Location = New-Object System.Drawing.Point(16, 182)
$txtDisc.Size = New-Object System.Drawing.Size(580, 24)
$txtDisc.Anchor = [System.Windows.Forms.AnchorStyles]::Top -bor [System.Windows.Forms.AnchorStyles]::Left -bor [System.Windows.Forms.AnchorStyles]::Right
$form.Controls.Add($txtDisc)

$btnBrowse = New-Object System.Windows.Forms.Button
$btnBrowse.Text = 'Browse...'
$btnBrowse.Location = New-Object System.Drawing.Point(604, 181)
$btnBrowse.Size = New-Object System.Drawing.Size(130, 26)
$btnBrowse.Anchor = [System.Windows.Forms.AnchorStyles]::Top -bor [System.Windows.Forms.AnchorStyles]::Right
$form.Controls.Add($btnBrowse)

# --- Launch / Exit / Status ---------------------------------------------------
$btnLaunch = New-Object System.Windows.Forms.Button
$btnLaunch.Text = 'Launch Game'
$btnLaunch.Location = New-Object System.Drawing.Point(16, 232)
$btnLaunch.Size = New-Object System.Drawing.Size(140, 32)
$form.Controls.Add($btnLaunch)

$btnExit = New-Object System.Windows.Forms.Button
$btnExit.Text = 'Exit'
$btnExit.Location = New-Object System.Drawing.Point(594, 232)
$btnExit.Size = New-Object System.Drawing.Size(140, 32)
$btnExit.Anchor = [System.Windows.Forms.AnchorStyles]::Top -bor [System.Windows.Forms.AnchorStyles]::Right
$form.Controls.Add($btnExit)

$lblStatus = New-Object System.Windows.Forms.Label
$lblStatus.Text = ''
$lblStatus.Location = New-Object System.Drawing.Point(16, 276)
$lblStatus.Size = New-Object System.Drawing.Size(720, 56)
$lblStatus.ForeColor = [System.Drawing.Color]::FromArgb(0, 90, 0)
$lblStatus.AutoSize = $false
$form.Controls.Add($lblStatus)

# --- Pre-populate from saved config ------------------------------------------
$cfg = Read-Config
if ($cfg) {
    if ($cfg.disc_path -and (Test-Path $cfg.disc_path)) {
        $txtDisc.Text = [string]$cfg.disc_path
    }
    $mode = [string]$cfg.bios_mode
    if ($mode -eq 'custom') {
        $rbCustom.Checked = $true
        if ($cfg.custom_bios_path) {
            $txtCustomBios.Text = [string]$cfg.custom_bios_path
        }
    } else {
        $rbOpenBIOS.Checked = $true
    }
}

# --- Event handlers -----------------------------------------------------------
$btnBrowse.Add_Click({
    $dlg = New-Object System.Windows.Forms.OpenFileDialog
    $dlg.Title = 'Select your legally obtained Ridge Racer Type 4 disc image'
    $dlg.Filter = 'CUE files (*.cue)|*.cue|All files (*.*)|*.*'
    $dlg.FilterIndex = 1
    $dlg.CheckFileExists = $true
    if ($txtDisc.Text -and (Test-Path (Split-Path -Parent $txtDisc.Text))) {
        $dlg.InitialDirectory = Split-Path -Parent $txtDisc.Text
    }
    $res = $dlg.ShowDialog($form)
    if ($res -eq [System.Windows.Forms.DialogResult]::OK) {
        $txtDisc.Text = $dlg.FileName
    }
})

$btnBrowseBios.Add_Click({
    $dlg = New-Object System.Windows.Forms.OpenFileDialog
    $dlg.Title = 'Select your legally obtained PS1 BIOS'
    $dlg.Filter = 'PS1 BIOS (*.bin)|*.bin|All files (*.*)|*.*'
    $dlg.FilterIndex = 1
    $dlg.CheckFileExists = $true
    if ($txtCustomBios.Text -and (Test-Path (Split-Path -Parent $txtCustomBios.Text))) {
        $dlg.InitialDirectory = Split-Path -Parent $txtCustomBios.Text
    }
    $res = $dlg.ShowDialog($form)
    if ($res -eq [System.Windows.Forms.DialogResult]::OK) {
        $txtCustomBios.Text = $dlg.FileName
    }
})

function Show-Error {
    param([string]$Message)
    $lblStatus.ForeColor = [System.Drawing.Color]::FromArgb(180, 0, 0)
    $lblStatus.Text = $Message
    [System.Windows.Forms.MessageBox]::Show($form, $Message, 'Ridge Racer 4 Launcher', 'OK', 'Warning') | Out-Null
}

$btnLaunch.Add_Click({
    $lblStatus.ForeColor = [System.Drawing.Color]::FromArgb(0, 90, 0)
    $lblStatus.Text = ''

    if (-not (Test-Path -LiteralPath $recompExePath -PathType Leaf)) {
        Show-Error "Recompiled executable not found:
$recompExePath
Make sure the release folder is intact."
        return
    }

    # --- Validate CUE
    $cuePath = $txtDisc.Text.Trim()
    if ([string]::IsNullOrEmpty($cuePath)) {
        Show-Error 'Please select your legally obtained game disc CUE file first.'
        return
    }
    if (-not (Test-Path -LiteralPath $cuePath -PathType Leaf)) {
        Show-Error "The selected CUE file does not exist:
$cuePath"
        return
    }

    if ([System.IO.Path]::GetExtension($cuePath) -ine '.cue') {
        Show-Error 'Select the .cue file, not an individual .bin track.'
        return
    }
    # Resolve user-entered relative paths before changing the child's directory.
    $cuePath = (Resolve-Path -LiteralPath $cuePath).ProviderPath

    # --- Resolve BIOS
    $useCustom = $rbCustom.Checked
    $customBiosPath = $null
    if ($useCustom) {
        $customBiosPath = $txtCustomBios.Text.Trim()
        if ([string]::IsNullOrEmpty($customBiosPath)) {
            Show-Error 'Custom BIOS is selected. Please choose a legally obtained PS1 BIOS file (e.g. SCPH1001.BIN).'
            return
        }
        if (-not (Test-Path -LiteralPath $customBiosPath -PathType Leaf)) {
            Show-Error "The selected BIOS file does not exist:
$customBiosPath"
            return
        }
    } elseif (-not (Test-Path -LiteralPath $bundledBiosPath -PathType Leaf)) {
        Show-Error "OpenBIOS is selected, but the bundled BIOS was not found at:
$bundledBiosPath
This release is missing OpenBIOS. See README.md for the required layout.
Restore bios\openbios.bin from the pinned PSXRecomp submodule with its license,
or select Custom BIOS and browse to your own legally obtained supported dump."
        return
    }

    if ($useCustom) {
        $customBiosPath = (Resolve-Path -LiteralPath $customBiosPath).ProviderPath
        $biosPath = $customBiosPath
    } else {
        $biosPath = (Resolve-Path -LiteralPath $bundledBiosPath).ProviderPath
    }

    # --- Persist config
    try {
        Write-Config -DiscPath $cuePath -BiosMode ($(if ($useCustom) { 'custom' } else { 'openbios' })) -CustomBiosPath $customBiosPath
    } catch {
        # Non-fatal.
    }

    # --- Build the runtime command line
    # Always pass the selected BIOS explicitly. The CUE directory is intentionally
    # the working directory; it must not change which BIOS the runtime loads.
    $argList = @('--bios', $biosPath, '--disc', $cuePath)

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $recompExePath
    $argSb = New-Object System.Text.StringBuilder
    for ($i = 0; $i -lt $argList.Count; $i++) {
        if ($i -gt 0) { [void]$argSb.Append(' ') }
        $a = $argList[$i]
        if ($a -match '\s') {
            [void]$argSb.Append('"').Append($a).Append('"')
        } else {
            [void]$argSb.Append($a)
        }
    }
    $psi.Arguments = $argSb.ToString()
    # IMPORTANT: use the directory containing the selected CUE as the working
    # directory so the CUE's relative FILE entries (track .bin files) resolve
    # correctly. Using the EXE's directory will fail for multi-track discs.
    $psi.WorkingDirectory = (Split-Path -Parent $cuePath)
    $psi.UseShellExecute = $false
    try {
        [System.Diagnostics.Process]::Start($psi) | Out-Null
    } catch {
        Show-Error "Failed to launch the game:
$_"
        return
    }
    $form.Close()
})

$btnExit.Add_Click({ $form.Close() })

[void]$form.ShowDialog()