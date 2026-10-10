# 9Drive Setup Assistant (Windows)

A dependency-free Python preflight helper for setting up the open-source 9Drive project locally on Windows.

## Run

1. Install Python 3.10+ and open PowerShell.
2. Download this folder or clone the Linkora repository.
3. Run the following command:

    py nine_drive_setup_assistant.py

The helper checks whether Git and Docker commands are available, whether Docker Engine responds, and—when launched from the 9Drive project folder—whether a .env file and expected variable names exist. It never prints secret values.

## What it does not do

- It does not install software, edit .env, start or stop containers, or connect Google accounts.
- It does not validate Google OAuth credentials with Google.
- It does not guarantee that the upstream 9Drive repository or its dependencies are secure.
- It does not replace reading the upstream README and Docker Compose configuration.

## Upstream links

- 9Drive: https://github.com/zenhosta/9drive
- Docker Desktop: https://www.docker.com/products/docker-desktop/
- Git for Windows: https://git-scm.com/downloads/win
- Google Cloud Console: https://console.cloud.google.com/
- Google Drive API: https://console.cloud.google.com/apis/library/drive.googleapis.com
- Google OAuth setup: https://console.cloud.google.com/auth/branding

## Security

Keep .env private and out of Git. Use unique strong secrets. The Google Drive scope https://www.googleapis.com/auth/drive is broad; begin with test accounts and review the exact scopes requested. For local testing, bind services to localhost and do not expose the dashboard or API to the public internet.
