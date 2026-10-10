# Windows Account Recovery Assistant

A beginner-friendly, standard-library-only Python helper for choosing safe, official Windows sign-in recovery paths.

## Safety scope
This utility is deliberately **read-only**. It does not reset or bypass passwords, change users, modify Windows system files, replace Ease of Access tools, unlock encrypted drives, or erase data. It optionally runs `manage-bde -status C:` to display BitLocker status.

## Requirements
- Python 3.9 or newer (no third-party packages)
- Windows for the optional BitLocker status check; the guidance menu also runs on other systems

## Run on Windows
1. Download `windows_recovery_assistant.py`.
2. Open Command Prompt or PowerShell in its folder.
3. Run:
   ```powershell
   py windows_recovery_assistant.py
   ```
4. Choose the option matching your account type.

## Official resources
- Microsoft account password reset: https://account.live.com/password/reset
- BitLocker recovery key: https://support.microsoft.com/windows/find-your-bitlocker-recovery-key
- Windows recovery options: https://support.microsoft.com/windows/recovery-options-in-windows
- Microsoft account help: https://support.microsoft.com/account-billing

## Important
If BitLocker is enabled and Windows asks for a recovery key, do not attempt to bypass encryption. Find the matching recovery key first. Some Windows recovery/reset options can remove apps or files, so read each screen carefully and back up accessible data.

This is a guidance utility, not a password-recovery guarantee. It does not replace Microsoft or your organization's official support.
