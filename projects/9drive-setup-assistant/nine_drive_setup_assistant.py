#!/usr/bin/env python3
"""Read-only preflight helper for a local 9Drive deployment on Windows."""
from __future__ import annotations
import shutil
import subprocess
from pathlib import Path

REPO_URL = "https://github.com/zenhosta/9drive.git"
REQUIRED_ENV = (
    "MYSQL_ROOT_PASSWORD", "MYSQL_DATABASE", "FRONTEND_URL", "VITE_API_URL",
    "JWT_ACCESS_SECRET", "TOKEN_ENCRYPTION_KEY", "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET", "GOOGLE_REDIRECT_URI",
)
WEAK_VALUES = {"", "changeme", "change_me", "your_password", "your_secret",
               "your_client_id", "your_client_secret", "password", "secret"}

def run_command(args: list[str]) -> tuple[bool, str]:
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=12)
        lines = (p.stdout or p.stderr).strip().splitlines()
        return p.returncode == 0, lines[0][:180] if lines else ("OK" if p.returncode == 0 else "Command failed")
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)

def find_repo() -> Path | None:
    here = Path.cwd().resolve()
    names = ("docker-compose.yml", "compose.yaml", "compose.yml", "docker-compose.yaml")
    for candidate in (here, *here.parents):
        if any((candidate / name).is_file() for name in names):
            return candidate
    return None

def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        for raw in path.read_text(encoding="utf-8-sig").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip("'").strip('"')
    except OSError:
        pass
    return values

def check_env(repo: Path) -> None:
    path = repo / ".env"
    print("\n[.env configuration]")
    if not path.is_file():
        print("  MISSING: .env was not found.")
        print("  In the 9Drive folder, run: Copy-Item .env.docker.example .env")
        return
    values = parse_env(path)
    missing = [key for key in REQUIRED_ENV if key not in values]
    weak = []
    for key in REQUIRED_ENV:
        if key not in values:
            continue
        value = values[key].strip()
        if key.startswith("GOOGLE_CLIENT_") and value == "":
            continue
        lowered = value.lower()
        if lowered in WEAK_VALUES or "your_" in lowered or "replace_me" in lowered:
            weak.append(key)
    print(f"  Found .env ({len(values)} variable(s)); secret values are not displayed.")
    print("  Missing expected variable names: " + ", ".join(missing) if missing else "  Expected variable names are present.")
    if weak:
        print("  Review placeholder/weak values for: " + ", ".join(weak))
    else:
        print("  No obvious placeholder values found in checked fields.")
    print("  Confirm .env is ignored by Git and never share or commit it.")
    print("  Keep frontend/API URLs localhost-only for a local test setup.")

def main() -> int:
    print("9Drive Setup Assistant — Windows preflight")
    print("Read-only checks only; no containers or files will be changed.\n")
    for label, command in (
        ("Git", ["git", "--version"]),
        ("Docker", ["docker", "--version"]),
        ("Docker Compose", ["docker", "compose", "version"]),
    ):
        if shutil.which(command[0]):
            ok, detail = run_command(command)
            print(f"[{'OK' if ok else 'CHECK'}] {label}: {detail}")
        else:
            print(f"[MISSING] {label}: command not found. Install it and reopen PowerShell.")
    ok, detail = run_command(["docker", "info", "--format", "{{.ServerVersion}}"])
    print(f"[{'OK' if ok else 'CHECK'}] Docker Engine: {detail if ok else 'Docker Desktop may be closed, starting, or not configured for Linux containers.'}")
    repo = find_repo()
    if repo:
        print(f"\n[Repository] Found likely project folder: {repo}")
        check_env(repo)
        ok, detail = run_command(["docker", "compose", "config", "--quiet"])
        if ok:
            print("\n[Compose file] Configuration parses successfully from the current directory.")
        else:
            print("\n[Compose file] Could not validate from the current directory.")
            print("  Open PowerShell in the 9Drive folder and run: docker compose config --quiet")
            if detail:
                print("  Docker reported: " + detail)
    else:
        print("\n[Repository] No Docker Compose project found in the current folder or its parents.")
        print("  Install Git, then in PowerShell run:")
        print(f"    git clone {REPO_URL}")
        print("    Set-Location 9drive")
        print("    Copy-Item .env.docker.example .env")
    print("\n[Next steps]")
    print("  1. Review the upstream README and Docker Compose configuration before running containers.")
    print("  2. Set strong, unique local secrets in .env; never paste them into chat or commit them.")
    print("  3. Configure Google OAuth after the local app is running and you understand requested scopes.")
    print("  4. Start manually when ready: docker compose up -d --build")
    print("  5. Guide URLs: http://localhost:5173 and http://localhost:4000")
    print("\nSecurity: the full Google Drive scope is broad. Use test accounts and do not expose ports publicly.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
