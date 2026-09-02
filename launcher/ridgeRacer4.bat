@echo off
rem Ridge Racer 4 Launcher
rem Starts the PowerShell-based GUI launcher in a hidden window.
rem The launcher locates the recompiled EXE and bundled OpenBIOS relative
rem to this script, so this .bat can be double-clicked from any location.

setlocal
set "SCRIPT_DIR=%~dp0"
set "PS_SCRIPT=%SCRIPT_DIR%ridgeRacer4.ps1"

if not exist "%PS_SCRIPT%" (
    echo ridgeRacer4.ps1 not found next to this .bat.
    pause
    exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%PS_SCRIPT%"
endlocal