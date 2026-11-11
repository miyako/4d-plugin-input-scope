"""Rebuild only proven native outputs; never discard packaged siblings."""

import argparse
from pathlib import Path
import re
import shutil


PRODUCT = "Input Scope"
BASE = Path("test/Plugins")
BUNDLE = BASE / (PRODUCT + ".bundle")
FILES = tuple(BUNDLE / relative for relative in (
    f"Contents/MacOS/{PRODUCT}", "Contents/Info.plist",
    "Contents/Resources/English.lproj/InfoPlist.strings",
    "Contents/Resources/constants.xlf", "Contents/Resources/manifest.json",
    "Contents/_CodeSignature/CodeResources",
))
WINDOWS_NAMES = (f"{PRODUCT}.4DX",)
WINDOWS_BINARY = BUNDLE / f"Contents/Windows64/{PRODUCT}.4DX"
DOWNLOADS = tuple(Path("winbuild") / name for name in WINDOWS_NAMES)
# Xcode puts XCBuildData under build/ or, with CONFIGURATION_BUILD_DIR, next to the product.
XCODE_DATA = (Path("build/XCBuildData"), BASE / "XCBuildData")
DIRECTORIES = (
    Path("build") / (PRODUCT + ".build"),
    Path("build/Default") / (PRODUCT + ".build"),
    BASE / (PRODUCT + ".build"),
    BASE / "Default" / (PRODUCT + ".build"),
)


def generated(path):
    return (path in set(map(str, (*FILES, WINDOWS_BINARY, *DOWNLOADS)))
            or bool(re.fullmatch(
                r"(?:build|test/Plugins)/XCBuildData/(?:build\.db(?:-wal|-shm)?|"
                r"[0-9a-f]{32}\.xcbuilddata/.+)", path))
            or any(path.startswith(str(directory) + "/")
                   for directory in DIRECTORIES))


def validate_paths(paths):
    root = Path.cwd().resolve()
    for path in paths:
        for parent in (path, *path.parents):
            if parent == Path("."):
                break
            if parent.is_symlink():
                raise ValueError(f"Refusing symlink output: {parent}")
        if not path.resolve().is_relative_to(root):
            raise ValueError(f"Output escapes checkout: {path}")
        if path.is_dir():
            for descendant in path.rglob("*"):
                if descendant.is_symlink():
                    raise ValueError(f"Refusing symlink output: {descendant}")


def prepare():
    files = FILES
    directories = DIRECTORIES
    validate_paths((*files, *directories, *XCODE_DATA))
    for path in files:
        if path.exists() and not path.is_file():
            raise ValueError(f"Expected generated file: {path}")
    for path in directories:
        if path.exists() and not path.is_dir():
            raise ValueError(f"Expected intermediate directory: {path}")
    for path in files:
        path.unlink(missing_ok=True)
    for path in directories:
        if path.exists():
            shutil.rmtree(path)


def require_file(path):
    validate_paths((path,))
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"Missing or empty native output: {path}")


def validate_outputs():
    validate_paths((*FILES, WINDOWS_BINARY, *DOWNLOADS, *DIRECTORIES, *XCODE_DATA))
    for path in FILES:
        require_file(path)

def validate_unsigned():
    validate_paths((*FILES, *DIRECTORIES, *XCODE_DATA))
    for path in FILES[:-1]:
        require_file(path)


def verify_resources():
    for name in ("manifest.json", "constants.xlf"):
        copied = BUNDLE / "Contents/Resources" / name
        require_file(copied)
        if copied.read_bytes() != Path(name).read_bytes():
            raise ValueError(f"Copied resource differs from source: {copied}")


def merge_windows():
    destinations = tuple(BUNDLE / "Contents/Windows64" / name for name in WINDOWS_NAMES)
    validate_paths((*DOWNLOADS, *destinations))
    for path in DOWNLOADS:
        require_file(path)
    for source, destination in zip(DOWNLOADS, destinations):
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)


def verify_windows():
    destinations = tuple(BUNDLE / "Contents/Windows64" / name for name in WINDOWS_NAMES)
    for source, destination in zip(DOWNLOADS, destinations):
        require_file(source)
        require_file(destination)
        if source.read_bytes() != destination.read_bytes():
            raise ValueError(f"Merged Windows payload differs from downloaded artifact: {destination}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("clean-macos", "verify-resources", "merge-windows"))
    phase = parser.parse_args().phase
    if phase == "clean-macos":
        prepare()
    elif phase == "merge-windows":
        merge_windows()
    else:
        validate_unsigned()
        verify_resources()
