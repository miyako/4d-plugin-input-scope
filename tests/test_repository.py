"""Raw-byte and POSIX-mode checks stay independent of Git's stat cache."""

from types import SimpleNamespace
import subprocess
from unittest.mock import patch

import yaml

from helper_support import GitFixture, ROOT, cwd
import repository


class RepositoryTests(GitFixture):
    def test_scoped_autocrlf_applies_before_real_checkout_without_host_config_writes(self):
        relative = "checkout-source.txt"
        (self.local / relative).write_bytes(b"first\nsecond\n")
        self.git("add", "--", relative)
        self.git("commit", "--quiet", "-m", "LF checkout fixture")
        private_global = self.root / "host-config-fixture"
        original_config = b"[core]\n\tautocrlf = true\n"
        private_global.write_bytes(original_config)
        workflow = yaml.load((ROOT / ".github/workflows/release.yml").read_text(),
                             Loader=yaml.BaseLoader)
        scoped = {key: workflow["env"][key] for key in
                  ("GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0")}
        self.assertEqual(scoped, {
            "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.autocrlf",
            "GIT_CONFIG_VALUE_0": "false",
        })
        for name, overrides, expected in (
            ("host-default", {}, b"first\r\nsecond\r\n"),
            ("workflow-scoped", scoped, b"first\nsecond\n"),
        ):
            destination = self.root / name
            result = subprocess.run(
                ["git", "clone", "--quiet", "--no-local", "--no-tags",
                 str(self.local), str(destination)],
                env={**self.env, "GIT_CONFIG_GLOBAL": str(private_global), **overrides},
                text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((destination / relative).read_bytes(), expected)
            self.assertEqual(private_global.read_bytes(), original_config)

    def test_windows_only_executable_bit_compatibility_still_checks_raw_bytes_and_index(self):
        relative = ".github/hooks/pre-push"
        target = self.local / relative
        expected = repository.actual_blob(target)
        self.assertEqual(expected[0], "100755")
        real_blob = repository.actual_blob

        def windows_blob(path):
            mode, oid = real_blob(path)
            return ("100644" if mode == "100755" else mode), oid

        with cwd(self.local), patch.object(repository, "actual_blob", side_effect=windows_blob):
            with self.assertRaisesRegex(ValueError, "Working source"):
                repository.verify_checkout(self.sha)
            with patch.object(repository, "sys", SimpleNamespace(platform="win32")):
                repository.verify_checkout(self.sha)
                target.write_bytes(target.read_bytes() + b"# raw mutation\n")
                with self.assertRaisesRegex(ValueError, "Working source"):
                    repository.verify_checkout(self.sha)
