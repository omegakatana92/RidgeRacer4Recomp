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


## Launcher (Windows)

A small Windows GUI launcher is included under `launcher\`:

* `launcher\ridgeRacer4.bat` â€” double-click to start.
* `launcher\ridgeRacer4.ps1` â€” the actual PowerShell + WinForms GUI.

The launcher lets you:

1. Pick your legally obtained Ridge Racer 4 `.cue` file (Browse...).
2. Choose **OpenBIOS (Included)** (the default) or **Custom BIOS** and point at your own legally obtained PS1 BIOS file.
3. Click **Launch Game**.

Your last selections (CUE path, BIOS mode, custom BIOS path) are remembered in
`%APPDATA%\%RidgeRacer4Recomp\launcher-config.json` and re-loaded the next time
the launcher starts.

The launcher resolves the recompiled executable and the bundled OpenBIOS
relative to its own location, so the release folder can be moved anywhere on
the PC without breaking the launch.

> **Why the launcher's working directory is the CUE's folder, not the build folder:** PSX CUE files frequently reference their track `.bin` files with relative `FILE` entries. The launched process therefore uses the directory containing the selected CUE as its working directory, so those relative `FILE` entries resolve.

The launcher is a thin convenience wrapper; it does **not** bundle, copy, or
distribute any game disc image, track, or retail BIOS.

## Building From Source

This repository contains the source code, build files, game configuration, and recompilation data required to build the project.

### Requirements

* Git
* CMake
* A supported C/C++ compiler
* Required project dependencies
* Your own legally obtained copy of the game, if required by the build process

### Clone the Repository

```bash
git clone https://github.com/omegakatana92/RidgeRacer4Recomp.git
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
