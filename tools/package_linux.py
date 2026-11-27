#!/usr/bin/env python3
"""Pack a built Linux AppDir into the release AppImage with the repo's AppRun and recomplauncher.json."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = 'usr/bin/Ridge_Racer_4_Recompiled'
PAYLOAD = 'usr/share/ridgeracer4recomp'


def stage(appdir: Path, dest: Path, root: Path = ROOT) -> None:
    """Copy appdir to dest, then put AppRun and recomplauncher.json at its top."""
    for name in [RUNTIME, f'{PAYLOAD}/game.toml', f'{PAYLOAD}/bios/openbios.bin']:
        if not (appdir / name).is_file():
            raise ValueError(f'Missing from the AppDir: {appdir / name}')
    for name in ['packaging/linux/AppRun', 'recomplauncher.json']:
        source = root / name
        if not source.is_file() or source.stat().st_size == 0:
            raise ValueError(f'Missing or empty release input: {source}')
    shutil.copytree(appdir, dest, symlinks=True)
    for name in ['AppRun', 'recomplauncher.json']:
        target = dest / name
        if target.is_symlink() or target.exists():
            target.unlink()
    shutil.copyfile(root / 'packaging/linux/AppRun', dest / 'AppRun')
    (dest / 'AppRun').chmod(0o755)
    shutil.copyfile(root / 'recomplauncher.json', dest / 'recomplauncher.json')


def package(appdir: Path, output: Path, appimagetool: str, root: Path = ROOT) -> None:
    if output.resolve().is_relative_to(appdir.resolve()):
        raise ValueError('Output must not be inside the AppDir.')
    with tempfile.TemporaryDirectory(prefix='r4-appdir-') as tmp:
        staged = Path(tmp) / 'AppDir'
        stage(appdir, staged, root)
        output.parent.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ, ARCH=os.environ.get('ARCH', 'x86_64'))
        subprocess.run([appimagetool, str(staged), str(output)], check=True, env=env)
    print(f'Created {output} with AppRun and recomplauncher.json. Extract it and run '
          'env -u APPIMAGE ./squashfs-root/AppRun once before publishing.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--appdir', type=Path, required=True,
                        help=f'Built AppDir with {RUNTIME} and {PAYLOAD}/')
    parser.add_argument('--output', type=Path, required=True, help='Destination AppImage')
    parser.add_argument('--appimagetool', default='appimagetool', help='appimagetool to run')
    args = parser.parse_args()
    try:
        package(args.appdir, args.output, args.appimagetool)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'{error}\n')
