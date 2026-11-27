import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

APPRUN = Path(__file__).resolve().parents[1] / 'packaging/linux/AppRun'
STUB = '#!/bin/sh\n{ pwd; for a in "$@"; do printf "%s\\n" "$a"; done; } > "$STUB_OUT"\n'
# Stops the AppRun that called it on its second rename, like a start killed mid-copy.
MV_KILLER = '''#!/bin/sh
n=$(cat "$MV_COUNT" 2>/dev/null || echo 0); n=$((n + 1)); echo "$n" > "$MV_COUNT"
if [ "$n" -ge 2 ]; then kill -9 "$PPID"; exit 1; fi
exec /bin/mv "$@"
'''


@unittest.skipUnless(sys.platform.startswith('linux') and shutil.which('sh'), 'AppRun runs on Linux')
class AppRunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='R4 apprun '))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.appdir = self.tmp / 'install'
        payload = self.appdir / 'usr/share/ridgeracer4recomp'
        (payload / 'bios').mkdir(parents=True)
        (payload / 'bios/openbios.bin').write_bytes(b'fixture')
        (payload / 'game.toml').write_text('[game]\n')
        (payload / 'input.ini').write_text('payload input\n')
        (payload / 'keybinds.ini').write_text('payload keybinds\n')
        runtime = self.appdir / 'usr/bin/Ridge_Racer_4_Recompiled'
        runtime.parent.mkdir(parents=True)
        runtime.write_text(STUB)
        runtime.chmod(0o755)
        shutil.copy(APPRUN, self.appdir / 'AppRun')
        self.home = self.tmp / 'home'
        self.home.mkdir()
        self.old = self.home / '.local/share/RidgeRacer4Recomp'
        self.data = self.appdir / 'recompdata'
        self.out = self.tmp / 'run.txt'

    def run_apprun(self, launcher=True, extra_env=None, check=True):
        env = {'PATH': os.environ['PATH'], 'HOME': str(self.home), 'APPDIR': str(self.appdir),
               'STUB_OUT': str(self.out)}
        if launcher:
            self.data.mkdir(exist_ok=True)
            env.update(RECOMPLAUNCHER='1', RECOMPLAUNCHER_DATA=str(self.data))
        env.update(extra_env or {})
        if self.out.exists():
            self.out.unlink()
        result = subprocess.run(['sh', str(self.appdir / 'AppRun'), '--disc', '/games/r4.cue'],
                                env=env, cwd=str(self.tmp), capture_output=True, text=True)
        if check:
            self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def started(self):
        lines = self.out.read_text().splitlines()
        return Path(lines[0]), lines[1:]

    def make_old_data(self, card=b'old card'):
        (self.old / 'openbios').mkdir(parents=True, exist_ok=True)
        (self.old / 'openbios/state_1.pst').write_bytes(b'state')
        (self.old / 'card1.mcd').write_bytes(card)
        (self.old / 'card2.mcd').write_bytes(b'card two')
        (self.old / 'SLUS-00797.options').write_text('opt\n')
        (self.old / 'settings.toml').write_text('[video]\nfullscreen = 2\n')
        (self.old / 'input.ini').write_text('player input\n')

    def assert_plays_from_data(self):
        cwd, args = self.started()
        self.assertEqual(cwd, self.data)
        self.assertEqual(args, ['--game', str(self.data / 'game.toml'),
                                '--memcard-dir', str(self.data / 'saves'), '--disc', '/games/r4.cue'])
        self.assertTrue((self.data / '.copied-from-user-data').is_file())
        self.assertFalse((self.data / '.copy-journal').exists())

    def assert_plays_from_old(self):
        cwd, args = self.started()
        self.assertEqual(cwd, self.old)
        self.assertEqual(args, ['--game', str(self.old / 'game.toml'), '--disc', '/games/r4.cue'])

    def test_without_launcher_uses_the_usual_folder(self):
        self.run_apprun(launcher=False)
        self.assert_plays_from_old()
        self.assertFalse(self.data.exists())
        self.assertEqual((self.old / 'input.ini').read_text(), 'payload input\n')

    def test_fresh_start_plays_from_launcher_data(self):
        self.run_apprun()
        self.assert_plays_from_data()
        self.assertTrue((self.data / 'saves').is_dir())
        self.assertFalse(self.old.exists())

    def test_old_data_is_copied_and_old_settings_win_once(self):
        self.make_old_data()
        self.data.mkdir()
        (self.data / 'settings.toml').write_text('[video]\nfullscreen = 0\n')
        self.run_apprun()
        self.assert_plays_from_data()
        self.assertEqual((self.data / 'settings.toml').read_text(), '[video]\nfullscreen = 2\n')
        self.assertEqual((self.data / 'saves/card1.mcd').read_bytes(), b'old card')
        self.assertEqual((self.data / 'saves/card2.mcd').read_bytes(), b'card two')
        self.assertEqual((self.data / 'saves/SLUS-00797.options').read_text(), 'opt\n')
        self.assertEqual((self.data / 'saves/openbios/state_1.pst').read_bytes(), b'state')
        self.assertEqual((self.data / 'input.ini').read_text(), 'player input\n')
        self.assertEqual((self.old / 'card1.mcd').read_bytes(), b'old card')
        self.assertEqual(list(self.data.glob('**/*.part')), [])
        # Done once: later changes in the old folder and the launcher's settings stay apart.
        (self.old / 'card1.mcd').write_bytes(b'newer old card')
        (self.data / 'settings.toml').write_text('[video]\nfullscreen = 1\n')
        self.run_apprun()
        self.assert_plays_from_data()
        self.assertEqual((self.data / 'saves/card1.mcd').read_bytes(), b'old card')
        self.assertEqual((self.data / 'settings.toml').read_text(), '[video]\nfullscreen = 1\n')

    @unittest.skipIf(hasattr(os, 'geteuid') and os.geteuid() == 0, 'root reads unreadable files')
    def test_failed_copy_plays_from_old_folder_then_retries(self):
        self.make_old_data()
        (self.old / 'card2.mcd').chmod(0)
        self.addCleanup((self.old / 'card2.mcd').chmod, 0o644)
        result = self.run_apprun()
        self.assertIn('could not copy', result.stderr)
        self.assert_plays_from_old()
        self.assertFalse((self.data / '.copied-from-user-data').exists())
        self.assertFalse((self.data / '.copy-journal').exists())
        self.assertFalse((self.data / 'saves/card1.mcd').exists())
        self.assertFalse((self.data / 'settings.toml').exists())
        (self.old / 'card2.mcd').chmod(0o644)
        (self.old / 'card1.mcd').write_bytes(b'saved after the failed copy')
        self.run_apprun()
        self.assert_plays_from_data()
        self.assertEqual((self.data / 'saves/card1.mcd').read_bytes(), b'saved after the failed copy')

    def test_interrupted_copy_is_taken_back_and_finished_next_start(self):
        self.make_old_data()
        shim = self.tmp / 'shim'
        shim.mkdir()
        (shim / 'mv').write_text(MV_KILLER)
        (shim / 'mv').chmod(0o755)
        result = self.run_apprun(check=False, extra_env={
            'PATH': f'{shim}:{os.environ["PATH"]}', 'MV_COUNT': str(self.tmp / 'mv-count')})
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.out.exists())
        self.assertFalse((self.data / '.copied-from-user-data').exists())
        self.assertTrue((self.data / '.copy-journal').exists())
        (self.old / 'card1.mcd').write_bytes(b'saved after the cut-off copy')
        self.run_apprun()
        self.assert_plays_from_data()
        self.assertEqual((self.data / 'saves/card1.mcd').read_bytes(), b'saved after the cut-off copy')
        self.assertEqual((self.data / 'settings.toml').read_text(), '[video]\nfullscreen = 2\n')
        self.assertEqual(list(self.data.glob('**/*.part')), [])

    def test_game_override_still_wins(self):
        own = self.tmp / 'own'
        self.run_apprun(extra_env={'RIDGERACER4_DATA_DIR': str(own)})
        cwd, args = self.started()
        self.assertEqual((cwd, args[:2]), (own, ['--game', str(own / 'game.toml')]))
        self.assertNotIn('--memcard-dir', args)


if __name__ == '__main__':
    unittest.main()
