# WinForge automation packaging standard

When a requested Windows task cannot be implemented reliably as a single standalone BAT file, deliver a complete Python automation app instead.

## Required deliverables
- A working Python application with a clear entry point.
- A Windows `.bat` launcher that checks for Python/dependencies and starts the app with useful error messages.
- A `requirements.txt` when third-party packages are needed.
- A `README.txt` with simple setup/use instructions, prerequisites, expected behavior, and troubleshooting.
- Any required config/assets/examples, with secrets and machine-specific paths excluded.
- A ZIP containing the complete runnable project, ready for the user to extract and run.

## Quality checks
- Prefer standard-library Python where practical; avoid unnecessary dependencies.
- Never overwrite or delete user data without clear confirmation and backups where appropriate.
- Do not embed passwords, API keys, or other secrets.
- Validate inputs, handle errors, and explain required permissions.
- Test the Python syntax and inspect the ZIP contents before publishing.
- Keep the launcher and instructions beginner-friendly; user-facing instructions can be in Bangla when that best fits the user.
- Commit the actual ZIP and supporting files to the repository, then add a library card with the correct direct download path. The card should identify the package as a ZIP and summarize what it contains.
- For simple tasks, continue to provide a single BAT file rather than overengineering it.

## Website behavior
Library cards must support downloads with different file extensions, including `.bat` and `.zip`. The download button label should reflect the actual file extension.
