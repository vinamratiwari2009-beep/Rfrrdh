# FF Guild API — Safe Starter

This is a minimal Vercel-compatible Flask starter.

## Endpoints
- `GET /` — service information
- `GET /health` — health check
- `GET /join?guildid=123&uid=456` — validates required identifiers, but does not perform a guild join

## Important
This package intentionally does **not** collect, transmit, or exchange game account passwords with a third-party JWT service, and it does not call private game endpoints. Use official, authorized APIs and an authentication flow that does not expose users' passwords.

## Deploy
1. Push this folder to a GitHub repository.
2. Import the repository into Vercel.
3. Deploy using the included `vercel.json`.
