"""Narrow macOS cleanup and final-only output retention."""

import shutil
from unittest import mock

from helper_support import Fixture, GitFixture, cwd
import native
import repository


class NativePreparationTests(Fixture):
    def test_selective_cleanup_preserves_resources_dependencies_and_default_siblings(self):
        protected = (
            native.BUNDLE / "Contents/QuickLook/Thumbnail.png",
            native.BUNDLE / "Contents/MacOS/runtime.dylib",
            native.BUNDLE / "Contents/Resources/custom.txt",
            native.BASE / "Default/Input Scope.bundle/Contents/Info.plist",
            native.BASE / "Default/keep", native.BASE / "Other.bundle/keep",
            "build/unrelated/keep", "lib/windows64/jsoncpp.lib", "include/json/json.h",
        )
        for path in protected:
            self.write(path, b"preserved")
        for path in native.FILES:
            self.write(path, b"stale")
        for path in native.DIRECTORIES:
            self.write(path / "intermediate", b"stale")
        with cwd(self.root):
            native.prepare()
            native.prepare()
        for path in protected:
            self.assertEqual((self.root / path).read_bytes(), b"preserved")
        for path in (*native.FILES, *native.DIRECTORIES):
            self.assertFalse((self.root / path).exists(), path)

    def test_symlink_anywhere_prevalidated_before_first_deletion(self):
        for where in (native.FILES[-1], native.DIRECTORIES[-1], native.BUNDLE,
                      native.DIRECTORIES[0] / "nested/link"):
            with self.subTest(where=where):
                first = self.write(native.FILES[0], b"must remain")
                destination = self.write("outside/keep", b"untouched")
                link = self.root / where
                if link.is_dir():
                    shutil.rmtree(link)
                link.parent.mkdir(parents=True, exist_ok=True)
                link.symlink_to(destination)
                with cwd(self.root), self.assertRaisesRegex(ValueError, "symlink"):
                    native.prepare()
                if where != native.BUNDLE:
                    self.assertEqual(first.read_bytes(), b"must remain")
                self.assertEqual(destination.read_bytes(), b"untouched")
                link.unlink()

    def test_cleanup_io_error_is_fatal(self):
        self.write(native.FILES[0], b"stale")
        with cwd(self.root), mock.patch("pathlib.Path.unlink", side_effect=PermissionError("denied")):
            with self.assertRaises(PermissionError):
                native.prepare()
        self.write(native.DIRECTORIES[0] / "stale", b"stale")
        with cwd(self.root), mock.patch("shutil.rmtree", side_effect=PermissionError("denied")):
            with self.assertRaises(PermissionError):
                native.prepare()

    def test_all_target_types_are_prevalidated_before_any_deletion(self):
        first = self.write(native.FILES[0], b"must remain")
        for path in (native.FILES[-1], native.DIRECTORIES[-1]):
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            if path in native.FILES:
                target.mkdir()
            else:
                target.write_bytes(b"not an intermediate directory")
            with cwd(self.root), self.assertRaisesRegex(ValueError, "Expected"):
                native.prepare()
            self.assertEqual(first.read_bytes(), b"must remain")
            target.rmdir() if target.is_dir() else target.unlink()

    def test_unsigned_gate_does_not_require_signature_but_final_gate_does(self):
        for path in native.FILES[:-1]:
            self.write(path, b"fresh unsigned output")
        with cwd(self.root):
            native.validate_unsigned()
            with self.assertRaisesRegex(ValueError, "Missing or empty"):
                native.validate_outputs()
        self.write(native.FILES[-1], b"fresh signature")
        with cwd(self.root):
            native.validate_outputs()

    def test_resources_must_be_fresh_exact_source_copies(self):
        for name in ("constants.xlf", "manifest.json"):
            self.write(name, b"source")
            self.write(native.BUNDLE / "Contents/Resources" / name, b"source")
        with cwd(self.root):
            native.verify_resources()
            (native.BUNDLE / "Contents/Resources/constants.xlf").write_bytes(b"stale")
            with self.assertRaisesRegex(ValueError, "differs"):
                native.verify_resources()

    def test_xcode_data_is_not_recursively_cleaned(self):
        paths = (
            "build/XCBuildData/build.db",
            "build/XCBuildData/unexpected-source.cpp",
            "build/XCBuildData/evil.xcbuilddata/keep",
        )
        for path in paths:
            self.write(path, b"preserve original bytes")
        with cwd(self.root):
            native.prepare()
        for path in paths:
            self.assertEqual((self.root / path).read_bytes(), b"preserve original bytes")

    def test_exact_windows_artifact_merge_and_final_revalidation(self):
        for path in native.DOWNLOADS:
            self.write(path, b"fresh binary" if path.suffix == ".4DX" else b"runtime")
        for name in native.WINDOWS_NAMES[1:]:
            self.write(native.BUNDLE / "Contents/Windows64" / name, b"runtime")
        with cwd(self.root):
            native.merge_windows()
            native.verify_windows()
            self.assertEqual(native.WINDOWS_BINARY.read_bytes(), b"fresh binary")
            native.WINDOWS_BINARY.write_bytes(b"late substitution")
            with self.assertRaisesRegex(ValueError, "differs"):
                native.verify_windows()

    def test_windows_missing_empty_or_symlink_precedes_any_copy(self):
        for path in native.DOWNLOADS:
            self.write(path, b"fresh")
        for name in native.WINDOWS_NAMES:
            self.write(native.BUNDLE / "Contents/Windows64" / name, b"fresh")
        binary = self.root / native.WINDOWS_BINARY
        binary.write_bytes(b"previous")
        with cwd(self.root):
            native.DOWNLOADS[0].write_bytes(b"")
            with self.assertRaisesRegex(ValueError, "Missing or empty"):
                native.merge_windows()
            self.assertEqual(binary.read_bytes(), b"previous")
            native.DOWNLOADS[0].write_bytes(b"fresh")
            native.DOWNLOADS[0].unlink()
            external = self.write("outside/windows.4DX", b"fresh")
            native.DOWNLOADS[0].symlink_to(external)
            with self.assertRaisesRegex(ValueError, "symlink"):
                native.merge_windows()
            self.assertEqual(binary.read_bytes(), b"previous")
            native.DOWNLOADS[0].unlink()
            with self.assertRaisesRegex(ValueError, "Missing or empty"):
                native.merge_windows()
            self.assertEqual(binary.read_bytes(), b"previous")

    def test_final_packaged_output_validation_requires_every_nonempty_regular_leaf(self):
        for path in native.FILES:
            self.write(path, b"fresh output")
        with cwd(self.root):
            native.validate_outputs()
            for path in native.FILES:
                saved = path.read_bytes()
                path.unlink()
                with self.assertRaisesRegex(ValueError, "Missing or empty"):
                    native.validate_outputs()
                path.write_bytes(b"")
                with self.assertRaisesRegex(ValueError, "Missing or empty"):
                    native.validate_outputs()
                path.write_bytes(saved)


class GeneratedRetentionTests(GitFixture):
    def test_actual_xcode_database_wal_and_outputs_are_final_only(self):
        for relative in (
            *native.FILES,
            "build/XCBuildData/build.db", "build/XCBuildData/build.db-wal",
            "build/XCBuildData/build.db-shm",
            "build/XCBuildData/0123456789abcdef0123456789abcdef.xcbuilddata/build-request.json",
            "build/Input Scope.build/Default/Input Scope.build/Objects-normal/arm64/main.o",
            "build/Default/Input Scope.build/main.o",
        ):
            target = self.local / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"fresh native output")
        with cwd(self.local):
            with self.assertRaises(ValueError):
                repository.verify_checkout(self.sha, generated=native.generated)
            repository.verify_checkout(self.sha, generated=native.generated, final=True)

    def test_evil_siblings_and_protected_resource_never_gain_final_exemption(self):
        for relative in (
            "build/XCBuildData-evil/build.db",
            "build/XCBuildData/unexpected-source.cpp",
            "build/XCBuildData/build.db-evil",
            "build/XCBuildData/evil.xcbuilddata/build-request.json",
            "build/Input Scope.build-evil/main.o",
            "build/unexpected-source.cpp",
            "Objs/Release-evil/main.obj",
            "Objs/Debug/main.obj",
            "winbuild/nested/Input Scope.4DX",
            "test/Plugins/Default/Input Scope.bundle/Contents/Info.plist",
            str(native.BUNDLE / "Contents/QuickLook/Thumbnail.png"),
            str(native.BUNDLE / "Contents/MacOS/runtime.dylib"),
            str(native.BUNDLE / "Contents/Resources/custom.txt"),
            str(native.BUNDLE / "Contents/_CodeSignature/evil"),
        ):
            with self.subTest(relative=relative):
                target = self.local / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b"unexpected")
                with cwd(self.local), self.assertRaises(ValueError):
                    repository.verify_checkout(self.sha, generated=native.generated, final=True)
                target.unlink()
