import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('linux_packager', ROOT / 'tools/package_linux.py')
packager = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(packager)


class LinuxPackagingTests(unittest.TestCase):
    def test_stage_adds_apprun_and_manifest_and_keeps_the_rest(self):
        with tempfile.TemporaryDirectory(prefix='R4 appdir ') as tmp:
            appdir = Path(tmp) / 'AppDir'
            files = [packager.RUNTIME, f'{packager.PAYLOAD}/game.toml',
                     f'{packager.PAYLOAD}/bios/openbios.bin', 'AppRun', 'game.desktop']
            for name in files:
                path = appdir / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'fixture')  # synthetic data; no BIOS or game data in tests
            staged = Path(tmp) / 'staged'
            packager.stage(appdir, staged)
            self.assertEqual((staged / 'AppRun').read_bytes(), (ROOT / 'packaging/linux/AppRun').read_bytes())
            self.assertEqual((staged / 'recomplauncher.json').read_bytes(), (ROOT / 'recomplauncher.json').read_bytes())
            if os.name == 'posix':
                self.assertTrue(os.access(staged / 'AppRun', os.X_OK))
            self.assertEqual((staged / 'game.desktop').read_bytes(), b'fixture')
            self.assertEqual((appdir / 'AppRun').read_bytes(), b'fixture')
            self.assertFalse((appdir / 'recomplauncher.json').exists())
            for name in files[:3]:
                with self.subTest(missing=name):
                    path = appdir / name
                    path.unlink()
                    with self.assertRaisesRegex(ValueError, 'Missing from the AppDir'):
                        packager.stage(appdir, Path(tmp) / 'missing')
                    path.write_bytes(b'fixture')


if __name__ == '__main__':
    unittest.main()
