#!/usr/bin/env python3
"""Stage only explicit release files; never copy a developer's disc/BIOS folders."""
import argparse
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
# Git blob identity from psxrecomp commit 001ea94717874704a925b85be9739265e0d60477.
# Update deliberately when changing the framework pin; never accept a retail dump.
OPENBIOS_BLOB_SHA = 'f7597d11f2b29884d1105a5544009a150627d9a5'


def package(exe: Path, output: Path, root: Path = ROOT) -> None:
    files = {
        'Ridge_Racer_4_Recompiled.exe': exe,
        'game.toml': root / 'game.toml',
        'README.md': root / 'README.md',
        'launcher/ridgeRacer4.bat': root / 'launcher/ridgeRacer4.bat',
        'launcher/ridgeRacer4.ps1': root / 'launcher/ridgeRacer4.ps1',
        'bios/openbios.bin': root / 'psxrecomp/bios/openbios.bin',
        'bios/OpenBIOS.LICENSE': root / 'psxrecomp/bios/OpenBIOS.LICENSE',
    }
    for name, source in files.items():
        if not source.is_file() or source.stat().st_size == 0:
            raise ValueError(f'Missing or empty release input: {source} ({name}). '
                             'Initialize the pinned submodule with git submodule update --init --recursive.')
    if files['bios/openbios.bin'].stat().st_size != 512 * 1024:
        raise ValueError('Expected the pinned 512 KiB OpenBIOS image; do not substitute a retail BIOS.')
    bios = files['bios/openbios.bin'].read_bytes()
    blob_id = hashlib.sha1(b'blob ' + str(len(bios)).encode('ascii') + b'\0' + bios).hexdigest()
    if blob_id != OPENBIOS_BLOB_SHA:
        raise ValueError('OpenBIOS does not match the pinned framework image; refusing to package it.')
    if output.resolve() in {p.resolve() for p in files.values()}:
        raise ValueError('Output must not overwrite a release input.')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, source in files.items():
            archive.write(source, name)
    print(f'Created {output} with {len(files)} required files. Run the first-run smoke check before publishing.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, required=True, help='Built Windows runtime executable')
    parser.add_argument('--output', type=Path, required=True, help='Destination ZIP')
    args = parser.parse_args()
    try:
        package(args.exe, args.output)
    except ValueError as error:
        parser.exit(1, f'{error}\n')
