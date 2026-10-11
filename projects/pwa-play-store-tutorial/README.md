# Website to Play Store Tutorial

A self-contained, mobile-friendly, video-style tutorial page in Bengali. It uses browser speech synthesis for narration and includes scene navigation, captions, and official documentation links. Narration voice availability depends on the user's browser and installed voices.

## Hosted location
https://linkora-r5hm.onrender.com/projects/pwa-play-store-tutorial/

## Accuracy notes
- A PWA commonly uses a Web App Manifest and a registered Service Worker; simply creating files is not sufficient.
- The service-worker.js snippet shown is a minimal lifecycle example and does not implement offline caching.
- PWABuilder UI and Play Console requirements can change. The tutorial links current official documentation.
- An AAB package does not guarantee Play Store approval. Developer account, app listing, policy declarations, testing, review, and eligibility requirements may apply.

## Files
- index.html: complete interactive tutorial player, no frameworks or external dependencies.
