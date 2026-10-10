# USB Offline AI Starter Kit

A Windows preparation tool for running a local GGUF model from a USB drive using [Mozilla.ai's official llamafile project](https://github.com/mozilla-ai/llamafile).

## What it does

- Checks that the runtime is a Windows executable with "llamafile" in its filename and is below the Windows 4 GiB executable limit.
- Checks that the selected model has a .gguf extension and begins with the GGUF signature.
- Copies the runtime and model into the USB destination as llamafile.exe and model.gguf.
- Generates a Windows Start.bat launcher and a README.txt.
- Uses Python's standard library only. No package installation is needed.
- After preparing the USB, Python is not required to run the generated launcher.

## Requirements

- Windows PC to run the generated Start.bat.
- Python 3.10+ on the preparation PC only.
- A compatible llamafile Windows executable and a compatible GGUF model.
- Enough free USB space for both files plus working headroom.
- Available RAM for the selected model and context size.

## Prepare the USB

Download the executable from the [official llamafile releases](https://github.com/mozilla-ai/llamafile/releases) and get a compatible GGUF model from a trusted publisher.

Run this from Command Prompt or PowerShell, updating the file paths and USB drive:

    python setup_usb_ai.py --exe "C:\Downloads\llamafile-0.10.6.exe" --model "C:\Downloads\my-model.gguf" --dest E:\OfflineAI

To set a different suggested context size:

    python setup_usb_ai.py --exe "C:\Downloads\llamafile-0.10.6.exe" --model "C:\Downloads\my-model.gguf" --dest E:\OfflineAI --ctx-size 4096

Supported context sizes: 1024, 2048, 4096, 8192, 16384, and 32768. The generated launcher will still ask which size to use each time, defaulting to the value specified during setup.

If the destination already has output files, the script stops instead of overwriting them. Use --overwrite only when you intend to replace those files.

## Run the AI

1. Safely eject the USB after setup has finished.
2. On a Windows computer, open the USB's OfflineAI folder.
3. Double-click Start.bat.
4. Choose a context size, or press Enter for the suggested default.
5. Wait for the server-ready message, then open **http://127.0.0.1:8080**.
6. Keep the terminal window open while chatting. Press Ctrl+C to stop the local server.

The launcher explicitly binds to 127.0.0.1, so the chat server is intended to be accessible only from that same computer, not other devices on the network.

## Troubleshooting

- Insufficient memory: close other programs and try a lower context size, such as 1024 or 2048.
- Missing files: keep llamafile.exe and model.gguf beside Start.bat in the destination folder.
- Model rejected: re-download the model from its trusted source and ensure it is a GGUF file, not an HTML error page renamed to .gguf.
- Server fails to start: confirm that the executable is a compatible Windows build and consult the official release documentation.

## Security notes

Only run executable files from sources you trust. The helper checks file names, size, and the GGUF signature; it does not prove publisher identity, model quality, compatibility, or safety. A domain resolving in DNS also does not prove that a website is trustworthy.

- Official project: https://github.com/mozilla-ai/llamafile
- Official releases: https://github.com/mozilla-ai/llamafile/releases
