# Linkora Tutorial Video Studio

A small Python API that turns a user-provided Bengali tutorial transcript into a narrated MP4 with title cards. It uses gTTS for Bengali narration and FFmpeg for MP4 encoding.

## Run locally
Install FFmpeg and Noto Sans Bengali fonts, then:
```bash
pip install -r requirements.txt
python server.py
```

POST `/api/generate` JSON: `{"title":"Tutorial title","transcript":"Paragraph one...\\n\\nParagraph two..."}`.
The response includes a playable MP4 URL. Transcript limit: 12,000 characters; up to 18 scenes.

## Deployment / storage caveat
Render's default filesystem is ephemeral. Generated videos are temporarily served for up to 12 hours and can disappear when the service restarts/redeploys. This starter does NOT claim permanent publishing. To archive videos permanently, configure an object-storage bucket (for example Cloudflare R2 or Supabase Storage) and credentials before enabling permanent publish. gTTS needs outbound internet access.
