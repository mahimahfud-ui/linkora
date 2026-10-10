#!/usr/bin/env python3
"""Prepare a Windows USB folder for offline AI with llamafile + a GGUF model."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

CONTEXT_SIZES = (1024, 2048, 4096, 8192, 16384, 32768)
WINDOWS_EXE_LIMIT = 4 * 1024**3
EXE_TARGET = "llamafile.exe"
MODEL_TARGET = "model.gguf"
BAT_TARGET = "Start.bat"
README_TARGET = "README.txt"

BAT_TEMPLATE = r"""@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title USB Offline AI - llamafile

if not exist "llamafile.exe" (
  echo ERROR: llamafile.exe is missing from this folder.
  pause
  exit /b 1
)
if not exist "model.gguf" (
  echo ERROR: model.gguf is missing from this folder.
  pause
  exit /b 1
)

echo.
echo ============================================
echo       USB OFFLINE AI - LOCAL ONLY
echo ============================================
echo This server binds to 127.0.0.1 on this PC.
echo Keep this window open while you chat.
echo.

set "CTX="
set /p "CTX=Context size [1024/2048/4096/8192/16384/32768] (default __DEFAULT_CTX__): "
if not defined CTX set "CTX=__DEFAULT_CTX__"
set "CTX_OK="
for %%C in (1024 2048 4096 8192 16384 32768) do if "%CTX%"=="%%C" set "CTX_OK=1"
if not defined CTX_OK (
  echo Invalid context size. Choose one of the listed values.
  pause
  exit /b 2
)

echo.
echo When llamafile reports that the server is ready, open:
echo http://127.0.0.1:8080
echo Stop the server with Ctrl+C.
echo.
"llamafile.exe" --server --host 127.0.0.1 --port 8080 --model "model.gguf" --ctx-size %CTX%
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" echo The AI process exited with code %RC%. Try a lower context size.
pause
exit /b %RC%
"""

README_TEMPLATE = """USB Offline AI Starter Kit
=========================

WHAT THIS DOES
- Checks that the runtime is a Windows .exe and smaller than 4 GiB.
- Checks the model extension and GGUF file signature.
- Copies them into the selected USB folder as llamafile.exe and model.gguf.
- Creates Start.bat and README.txt.
- Uses only Python's standard library; no pip install is required.
- After setup, Start.bat runs without Python.

PREPARE THE USB
1. Download a Windows-compatible llamafile executable from:
   https://github.com/mozilla-ai/llamafile/releases
2. Download a compatible GGUF model from its trusted publisher.
3. On a PC with Python 3.10+, run this from a terminal:

   python setup_usb_ai.py --exe "C:\\Downloads\\llamafile-0.10.6.exe" --model "C:\\Downloads\\my-model.gguf" --dest E:\\OfflineAI

   Change these paths to match your files and USB drive. Use --ctx-size 4096
   to change the suggested default. Supported values: 1024, 2048, 4096, 8192,
   16384, 32768. Higher context sizes need more memory.

4. Open the destination folder on the USB and double-click Start.bat.
5. Wait until the server reports it is ready, then open:
   http://127.0.0.1:8080
6. Keep the command window open while chatting. Press Ctrl+C to stop it.

SECURITY AND LIMITATIONS
- Download executable files only from sources you trust. Check release notes
  and publisher details before running them.
- The generated launcher binds to 127.0.0.1, so it is intended for this
  computer, not for other devices on your network.
- The model must be a compatible GGUF file. This helper checks the signature,
  not model quality, authenticity, compatibility, or safety.
- If you see an insufficient-memory error, restart and try a lower context size.
- The AI can run offline once the runtime and model are already on the USB.
- Python is needed on the preparation PC only; the final launcher does not
  require Python or an internet connection.

OPTIONS
  --exe PATH       Path to the downloaded llamafile .exe
  --model PATH     Path to the GGUF model
  --dest PATH      Folder on the USB where the files will be prepared
  --ctx-size N     Suggested default context size (default: 2048)
  --overwrite      Allow replacing existing generated files
"""

def fail(message: str) -> "None":
    raise SystemExit(f"ERROR: {message}")


def existing_file(raw: str, label: str) -> Path:
    path = Path(raw).expanduser().resolve()
    if not path.is_file():
        fail(f"{label} file not found: {path}")
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare a USB folder for offline llamafile + GGUF use."
    )
    parser.add_argument("--exe", required=True, help="Path to the llamafile Windows .exe")
    parser.add_argument("--model", required=True, help="Path to a compatible GGUF model")
    parser.add_argument("--dest", required=True, help="Destination folder on the USB drive")
    parser.add_argument("--ctx-size", type=int, choices=CONTEXT_SIZES, default=2048,
                        help="Suggested default context size (default: 2048)")
    parser.add_argument("--overwrite", action="store_true",
                        help="Allow replacing files already present in the destination")
    return parser


def main() -> int:
    if sys.platform != "win32":
        print("Note: this helper creates a Windows Start.bat. Run it on Windows for normal use.")

    args = build_parser().parse_args()
    exe = existing_file(args.exe, "llamafile executable")
    model = existing_file(args.model, "GGUF model")

    if exe.suffix.lower() != ".exe" or "llamafile" not in exe.stem.lower():
        fail("The runtime file must be a Windows .exe with 'llamafile' in its filename.")
    if exe.stat().st_size >= WINDOWS_EXE_LIMIT:
        fail("The executable is 4 GiB or larger. Windows cannot run llamafile executables at or above this limit.")
    if model.suffix.lower() != ".gguf":
        fail("The model must have a .gguf extension.")
    if model.stat().st_size < 4:
        fail("The model file is too small to be a valid GGUF file.")
    with model.open("rb") as stream:
        if stream.read(4) != b"GGUF":
            fail("The model does not start with the GGUF signature. Check that the download completed.")

    dest = Path(args.dest).expanduser().resolve()
    if not dest.name or dest == Path(dest.anchor):
        fail("Choose a folder on the USB (for example E:\\OfflineAI), not the drive root.")
    dest.mkdir(parents=True, exist_ok=True)

    targets = {
        exe: dest / EXE_TARGET,
        model: dest / MODEL_TARGET,
    }
    generated = (dest / BAT_TARGET, dest / README_TARGET)
    conflicts = []
    for source, target in targets.items():
        if target.exists() and source.resolve() != target.resolve():
            conflicts.append(target.name)
    conflicts.extend(path.name for path in generated if path.exists())
    if conflicts and not args.overwrite:
        fail("Destination already contains: " + ", ".join(sorted(set(conflicts))) +
             ". Choose an empty folder or rerun with --overwrite.")

    bytes_to_copy = sum(
        source.stat().st_size
        for source, target in targets.items()
        if source.resolve() != target.resolve()
    )
    if shutil.disk_usage(dest).free < bytes_to_copy:
        fail("Not enough free space in the destination for the runtime and model.")

    try:
        for source, target in targets.items():
            if source.resolve() != target.resolve():
                shutil.copy2(source, target)
                print(f"Copied {source.name} -> {target.name}")
            else:
                print(f"Already in destination: {target.name}")

        bat = BAT_TEMPLATE.replace("__DEFAULT_CTX__", str(args.ctx_size))
        (dest / BAT_TARGET).write_text(bat, encoding="utf-8", newline="\r\n")
        (dest / README_TARGET).write_text(README_TEMPLATE, encoding="utf-8", newline="\r\n")
    except OSError as exc:
        fail(f"Could not prepare the USB folder: {exc}")

    print()
    print("USB Offline AI files are ready:")
    for name in (EXE_TARGET, MODEL_TARGET, BAT_TARGET, README_TARGET):
        print(f"  {dest / name}")
    print()
    print("Double-click Start.bat on Windows. Python is not needed after setup.")
    print("Local chat address: http://127.0.0.1:8080")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
