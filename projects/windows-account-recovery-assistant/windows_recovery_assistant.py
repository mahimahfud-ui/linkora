#!/usr/bin/env python3
"""Windows Account Recovery Assistant — safe, read-only guidance.

This utility does NOT reset or bypass passwords, modify Windows system files,
change accounts, or decrypt a drive. It helps you choose official recovery
options and optionally checks BitLocker status using Windows' built-in tool.
"""
from __future__ import annotations

import platform
import shutil
import subprocess
import sys
import webbrowser

MICROSOFT_RESET = "https://account.live.com/password/reset"
MICROSOFT_SIGNIN_HELP = "https://support.microsoft.com/account-billing"
BITLOCKER_HELP = "https://support.microsoft.com/windows/find-your-bitlocker-recovery-key"
WINDOWS_RECOVERY_HELP = "https://support.microsoft.com/windows/recovery-options-in-windows"

def pause() -> None:
    input("\nPress Enter to continue...")

def open_link(url: str) -> None:
    print(f"Opening: {url}")
    try:
        webbrowser.open(url)
    except Exception:
        print("Could not open a browser automatically. Copy this URL into your browser:")
        print(url)

def bitlocker_status() -> None:
    print("\n=== BitLocker status (read-only) ===")
    if platform.system() != "Windows":
        print("This check is available only on Windows.")
        return
    exe = shutil.which("manage-bde")
    if not exe:
        print("manage-bde was not found. Check BitLocker from Windows Settings or Control Panel.")
        return
    try:
        result = subprocess.run(
            [exe, "-status", "C:"],
            capture_output=True, text=True, timeout=15, check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        output = (result.stdout or result.stderr).strip()
        print(output if output else "Windows returned no status text.")
        print("\nThis command only reads status; it does not unlock or change encryption.")
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"Could not query status: {exc}")

def main() -> int:
    print("=" * 62)
    print(" WINDOWS ACCOUNT RECOVERY ASSISTANT")
    print(" Safe guidance only — no password bypass or system-file changes")
    print("=" * 62)
    if platform.system() != "Windows":
        print(f"Note: this computer reports {platform.system()}. Some checks require Windows.")
    print("\nChoose the account type you are trying to recover:")
    print("  1. Microsoft account (email address used to sign in)")
    print("  2. Local Windows account")
    print("  3. Work or school account")
    print("  4. Check BitLocker status (read-only)")
    print("  5. Windows recovery options")
    print("  0. Exit")
    while True:
        choice = input("\nSelect an option: ").strip()
        if choice == "1":
            print("\nMicrosoft account:")
            print("• Use Microsoft's official password reset page.")
            print("• Complete identity verification using a recovery method you control.")
            print("• If you cannot access verification methods, follow Microsoft's account recovery process.")
            open_link(MICROSOFT_RESET)
            pause()
        elif choice == "2":
            print("\nLocal account:")
            print("• At the sign-in screen, check for the built-in 'Reset password' option.")
            print("• If available, answer the security questions you configured for that account.")
            print("• If another administrator account on this PC is yours, use Windows' supported account-management options.")
            print("• If these options are unavailable, review official Windows recovery options before proceeding.")
            print("• Do not replace accessibility tools with Command Prompt or run unknown password-reset utilities.")
            open_link(WINDOWS_RECOVERY_HELP)
            pause()
        elif choice == "3":
            print("\nWork or school account:")
            print("• Contact your organization's IT administrator or use its approved self-service reset process.")
            open_link(MICROSOFT_SIGNIN_HELP)
            pause()
        elif choice == "4":
            bitlocker_status()
            print("\nIf the drive is locked, locate the recovery key using a Microsoft account, your organization, or the place where you saved it.")
            open_link(BITLOCKER_HELP)
            pause()
        elif choice == "5":
            print("\nBefore resetting Windows:")
            print("• Back up files if you can access them.")
            print("• Confirm whether BitLocker/device encryption is enabled and locate the recovery key.")
            print("• Read the official options carefully; some recovery choices remove apps or files.")
            open_link(WINDOWS_RECOVERY_HELP)
            pause()
        elif choice == "0":
            print("No system changes were made. Goodbye.")
            return 0
        else:
            print("Please enter one of the listed numbers.")

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, EOFError):
        print("\nExited. No system changes were made.")
        raise SystemExit(0)
