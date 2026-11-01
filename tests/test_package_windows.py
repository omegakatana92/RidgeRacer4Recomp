import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SPEC = importlib.util.spec_from_file_location('packager', Path(__file__).resolve().parents[1] / 'tools/package_windows.py')
packager = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(packager)


class PackagingTests(unittest.TestCase):
    def test_required_files_only_and_reject_missing_or_substituted_bios(self):
        with tempfile.TemporaryDirectory(prefix='R4 release ') as tmp:
            root = Path(tmp)
            required = ['game.toml', 'README.md', 'launcher/ridgeRacer4.bat',
                        'launcher/ridgeRacer4.ps1', 'psxrecomp/bios/openbios.bin',
                        'psxrecomp/bios/OpenBIOS.LICENSE', 'game.exe']
            bios = b'\0' * (512 * 1024)  # synthetic data; no BIOS or game data in tests
            for name in required:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(bios if name.endswith('openbios.bin') else b'fixture')
            for name in ['disc/private.bin', 'bios/SCPH1001.BIN', 'launcher-config.json']:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('must not be shipped')
            output = root / 'dist/release.zip'
            # A BIOS with the correct size but wrong identity must not ship.
            with self.assertRaisesRegex(ValueError, 'does not match'):
                packager.package(root / 'game.exe', output, root)
            self.assertFalse(output.exists())
            blob_id = hashlib.sha1(b'blob 524288\0' + bios).hexdigest()
            with patch.object(packager, 'OPENBIOS_BLOB_SHA', blob_id):
                packager.package(root / 'game.exe', output, root)
                with zipfile.ZipFile(output) as archive:
                    self.assertEqual(set(archive.namelist()), {
                        'Ridge_Racer_4_Recompiled.exe', 'game.toml', 'README.md',
                        'launcher/ridgeRacer4.bat', 'launcher/ridgeRacer4.ps1',
                        'bios/openbios.bin', 'bios/OpenBIOS.LICENSE'})
                    self.assertIsNone(archive.testzip())
                for name in required[:-1]:
                    with self.subTest(missing=name):
                        path = root / name
                        original = path.read_bytes()
                        path.unlink()
                        with self.assertRaisesRegex(ValueError, 'Missing or empty'):
                            packager.package(root / 'game.exe', root / 'missing.zip', root)
                        path.write_bytes(original)


if __name__ == '__main__':
    unittest.main()
