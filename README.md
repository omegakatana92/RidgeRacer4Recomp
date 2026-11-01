# Ridge Racer Type 4 - Recomp

> **Work in Progress:** This recompilation project is currently under development. Features, compatibility, performance, and functionality may change as development continues.

A modern fan-made recompilation project for **Ridge Racer Type 4**, originally released for the **Sony PlayStation**.

## Built With PSXRecomp

This project is built using [PSXRecomp](https://github.com/mstan/psxrecomp), the PlayStation 1 static recompiler framework created by mstan. The framework is included in this project as a Git submodule.

## Disc Required

This project **does not include the original game disc image or copyrighted assets**.

To play, you must provide your **own legally obtained copy** of *Ridge Racer Type 4*.

The original game disc image must **not** be uploaded to this repository or included with releases.

## Features

* PlayStation recompilation
* **Work in progress / actively being developed**
* Requires the user's own legally obtained game disc/image
* No copyrighted game disc files are distributed with this project
* No original game artwork, music, or other copyrighted game assets are included
* Fullscreen support
* Designed for modern systems
* Keyboard controls
* Source code intended to support community contributions
* Bug fixes and feature improvements welcome

## Controls

Controls depend on the current runtime configuration.

Keyboard and controller bindings may be configurable through the project's input configuration.


## First run: download versus source checkout

Download the platform asset from [Releases](https://github.com/omegakatana92/RidgeRacer4Recomp/releases).
GitHub's automatic **Source code** ZIP is not a runnable release and does not
contain Git submodule contents, generated code, or OpenBIOS.

**Original v1.0.0 Windows packaging problem (issue #2):**
Before the packaging repair, `Ridge_Racer_4_Recomp_Windows.zip` contained only
`Ridge_Racer_4_Recompiled.exe`. It omitted the external OpenBIOS image, launcher,
configuration, and instructions. The old “OpenBIOS (Included)” wording describes
an intended layout, not the original ZIP's contents. The release packaging
workflow replaces that download with the complete layout below; check the
release notes for its completion. If your ZIP contains just an EXE, re-download
it after the repair or use the manual repair steps below. The v1.0.0 Linux AppImage does contain
`bios/openbios.bin` and its license in its payload.

### Windows folder layout and setup

Extract the entire release into a writable folder; do not run inside the ZIP.
The Windows launcher expects this layout (the EXE and `bios/` are siblings of
`launcher/`, not inside it):

```text
RidgeRacer4Recomp/
  Ridge_Racer_4_Recompiled.exe
  game.toml
  README.md
  launcher/
    ridgeRacer4.bat
    ridgeRacer4.ps1
  bios/
    openbios.bin
    OpenBIOS.LICENSE
```

To repair the old Windows ZIP, keep its executable and copy `game.toml`,
`README.md`, and both `launcher/` files from this repository into the layout
above. For OpenBIOS, initialize this repository's pinned submodule:

```powershell
git clone --recurse-submodules https://github.com/omegakatana92/RidgeRacer4Recomp.git
# For an existing checkout, run inside it instead:
# git submodule update --init --recursive
```

Copy **only** `psxrecomp/bios/openbios.bin` and
`psxrecomp/bios/OpenBIOS.LICENSE` into the release's `bios/` directory.
Do not rename a retail BIOS to `openbios.bin`. Alternatively, choose Custom
BIOS in the launcher; that mode does not require `openbios.bin`.

1. Keep your own legally obtained game dump in a separate writable directory,
   for example `C:\Games\R4-disc\`. Keep the `.cue` and **every** referenced
   `.bin` track together, preserving the names and relative subfolders in the
   CUE's `FILE` entries. Do not put game files in `bios/` or upload them here.
   The project configuration targets the USA release, **SLUS-00797**; other
   regions/revisions are not established as compatible.
2. Double-click `launcher\ridgeRacer4.bat` (Windows PowerShell 5.1 and WinForms).
   Use Browse to select your `.cue`, not a track `.bin` or ZIP.
3. Select **OpenBIOS** if `bios\openbios.bin` is installed, or select **Custom
   BIOS**, then Browse to your own legally obtained supported PS1 BIOS dump.
   The launcher now reports OpenBIOS as available or missing rather than
   promising that every download includes it.
4. Click **Launch Game**. Missing files are reported with their expected paths.
   If the runtime rejects a custom BIOS, see the compatibility note below.

Selections are saved in `%APPDATA%\RidgeRacer4Recomp\launcher-config.json`;
if ApplicationData is unavailable, the fallback is `launcher-config.json`
beside the PowerShell script. Browse again after moving your game dump or
custom BIOS. Moving the whole release keeps its EXE/OpenBIOS paths valid.

The launcher resolves the EXE and OpenBIOS from the release root and passes
an **absolute `--bios` path in both modes**, plus an absolute `--disc` path.
It uses the selected CUE's directory as the child's working directory for
relative track references. BIOS discovery therefore does not depend on where
the disc is stored or where the launcher was opened.

For troubleshooting without the wrapper, open PowerShell and use absolute
paths (replace these examples with your actual paths):

```powershell
Set-Location 'C:\Games\R4-disc'
& 'C:\Games\RidgeRacer4Recomp\Ridge_Racer_4_Recompiled.exe' --bios 'C:\Games\RidgeRacer4Recomp\bios\openbios.bin' --disc 'C:\Games\R4-disc\R4.cue'
```

For a custom BIOS, replace the `--bios` value with its absolute path. Starting
from a terminal also makes runtime errors visible if the GUI closes quickly.

### OpenBIOS versus a custom BIOS

OpenBIOS is the PCSX-Redux project's freely licensed replacement BIOS, not a
Sony retail BIOS dump. Use the version supplied by the pinned PSXRecomp
submodule and retain `OpenBIOS.LICENSE` when redistributing it. Recompiled BIOS
code in an executable does not imply the external BIOS image was packaged.

Custom BIOS mode passes your selected dump to the runtime; it does not copy,
download, or redistribute it. A file existing on disk does **not** guarantee
compatibility: the runtime validates BIOS identity and the native BIOS
backends compiled into that build. The pinned framework recognizes SCPH1001
(512 KiB, CRC32 `37157331`), but a release may still require regeneration and
rebuilding for a different BIOS backend. If you see “not compiled into the
current build,” use the matching OpenBIOS image or rebuild with the supported
backend; renaming the file will not fix it. No retail BIOS is provided here.

### Linux / Steam Deck AppImage

The published v1.0.0 AppImage includes OpenBIOS and its license under
`usr/share/ridgeracer4recomp/bios/`. Its `AppRun` copies these into writable user
storage before launching. The default location is
`~/.local/share/RidgeRacer4Recomp`; `$XDG_DATA_HOME/RidgeRacer4Recomp` takes
precedence, and `RIDGERACER4_DATA_DIR` overrides both.

Keep your legal CUE/BIN dump outside the AppImage, for example in
`/home/deck/Games/R4-disc/`, with the same track-layout rules as Windows.
In Desktop Mode, mark the AppImage executable and launch with an absolute disc
path to override the development disc path in `game.toml`:

```bash
chmod +x '/home/deck/Downloads/Ridge_Racer_4_Recomp-v1.0.0-linux-x86_64.AppImage'
'/home/deck/Downloads/Ridge_Racer_4_Recomp-v1.0.0-linux-x86_64.AppImage' --disc '/home/deck/Games/R4-disc/R4.cue'
```

The runtime UI may also ask you to select the CUE. For Custom BIOS, append
`--bios '/absolute/path/to/your/BIOS.BIN'`; the same backend compatibility limits
apply. Do not replace the AppImage-managed `bios/openbios.bin` with a retail
dump: `AppRun` refreshes bundled BIOS files each launch. For Steam, add the
AppImage as a non-Steam game and put `--disc "/home/deck/Games/R4-disc/R4.cue"`
in Launch Options. Run once in Desktop Mode first to check any errors.

### Troubleshooting

* **OpenBIOS missing:** check the exact path shown by the Windows launcher.
  The original v1.0.0 Windows ZIP needs the repair steps above.
* **Executable missing:** preserve the folder tree; placing the launcher next
  to the EXE instead of under `launcher/` changes its expected root.
* **Disc/track missing:** select a CUE from your extracted dump, then check its
  `FILE` entries against all track filenames. A CUE alone contains no game data.
* **Custom BIOS rejected:** check runtime compatibility, not just its filename.
* **Still fails:** report your OS, release asset name, selected BIOS mode,
  folder layout, and terminal error text in issue #2. Do not attach disc images
  or retail BIOS files. These setup steps are not a guarantee of full playability.

### Packaging a Windows release (maintainers)

Initialize the pinned submodule, build the Windows runtime, then use Python 3:

```powershell
python tools/package_windows.py --exe 'build/Release/Ridge_Racer_4_Recompiled.exe' --output 'dist/Ridge_Racer_4_Recomp_Windows.zip'
```

Pass the actual executable output path if it differs. The script packages an
explicit list of required support files, using only the pinned submodule's
OpenBIOS image and license. It refuses missing/empty inputs and never copies
`disc/`, `input/`, user settings, or arbitrary BIOS folders. If the runtime build
needs additional redistributable dependencies, stage and verify those separately.

Before publishing, extract the ZIP into a clean folder with spaces in its
name, launch from a different working directory, and select a CUE stored
outside the release. Verify OpenBIOS mode, missing-OpenBIOS feedback, and
Custom BIOS selection (including a rejected/unsupported BIOS). Check that no
game dump or retail BIOS entered the archive. Rebuild the downloadable asset;
merging a README/launcher change alone cannot fix the old ZIP.

## Building From Source

This checkout contains build files, game configuration, and function seeds.
It does not contain `generated/` or `bios-generated/`, which CMake expects.
Initialize the pinned PSXRecomp submodule and generate the game and matching
OpenBIOS sources with that framework before configuring CMake. The commands
below are configure/build steps, not a complete generation recipe; a fresh
clone alone is not a ready-to-build or runnable release.

### Requirements

* Git
* CMake
* A supported C/C++ compiler
* Required project dependencies
* Your own legally obtained copy of the game, if required by the build process

### Clone the Repository

```bash
git clone --recurse-submodules https://github.com/omegakatana92/RidgeRacer4Recomp.git
cd RidgeRacer4Recomp
```

### Configure the Build

```bash
cmake -S . -B build
```

### Build

```bash
cmake --build build --config Release
```

The resulting executable will be placed in the project's build output directory.

**The original game disc image is not included in this repository.**

Because this project is currently under development, the build may not yet be fully functional or complete.

## Contributing

Contributions and improvements are welcome!

Developers can **fork this repository**, make changes, test their work, and submit a **Pull Request**.

Possible contributions include:

* Bug fixes
* Performance improvements
* Controller improvements
* Fullscreen improvements
* Linux compatibility
* Steam Deck compatibility
* Build-system improvements
* Accessibility improvements
* Documentation improvements
* Configuration options
* Additional platform support

Please do not submit copyrighted game disc images, game assets, music, artwork, or other proprietary game material.

## Copyright

**Ridge Racer Type 4**, its characters, names, artwork, music, trademarks, and other intellectual property remain the property of their respective copyright and trademark holders.

This is an independent fan-made recompilation project.

No original game disc images or copyrighted game assets are distributed with this project.

**All rights to the original game and its associated intellectual property remain with their respective owners.**

## Fullscreen

Fullscreen support is available through the runtime configuration.

## Disclaimer

This project is currently a **work in progress** and is not considered a finished or fully playable release.

This project does not distribute the original game disc image or copyrighted game assets.

Users must provide their own legally obtained copy of the game.

This project is an independent fan-made recompilation and is **not affiliated with or endorsed by the original game's rights holders.**
