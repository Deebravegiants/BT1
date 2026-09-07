# [H] OpenClaw Telegram webhook request bodies were read before secret validation, enabling unauthenticated resource exhaustion

## Summary
Severity: High
Advisory: GHSA-jq3f-vjww-8rq7
CVE: CVE-2026-32980
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-jq3f-vjww-8rq7
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.13

## Details
### Summary
`openclaw` versions `<= 2026.3.12` read and buffered Telegram webhook request bodies before validating `x-telegram-bot-api-secret-token`. This let unauthenticated callers force up to the configured webhook body limit of pre-auth body I/O and JSON parse work per request.

### Affected Packages / Versions
- Package: `openclaw` (`npm`)
- Affected versions: `<= 2026.3.12`
- Fixed version: `2026.3.13`

### Details
The vulnerable path was the standalone Telegram webhook listener in `src/telegram/webhook.ts`. In affected releases, the request handler accepted `POST` requests, called `readJsonBodyWithLimit(...)`, and only then checked the Telegram secret header. Because the secret validation happened after body reading, an unauthenticated caller could make the server spend memory, socket time, and JSON parse work on requests that should have been rejected before any body processing.

This issue is in scope under OpenClaw's trust model because the Telegram webhook endpoint accepts untrusted network traffic and the secret header is the authentication boundary for that ingress path.

### Fix
`openclaw@2026.3.13` validates the Telegram webhook secret before any body I/O. Current code reads the header, rejects invalid requests immediately with `401`, and only calls `readJsonBodyWithLimit(...)` after `hasValidTelegramWebhookSecret(...)` succeeds.

Regression coverage exists in `src/telegram/webhook.test.ts` (`rejects unauthenticated requests before reading the request body`).

### Fix Commit(s)
- `7e49e98f79073b11134beac27fdff547ba5a4a02`

Thanks @space08 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jq3f-vjww-8rq7
- https://nvd.nist.gov/vuln/detail/CVE-2026-32980
- https://github.com/openclaw/openclaw/commit/7e49e98f79073b11134beac27fdff547ba5a4a02
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-resource-exhaustion-via-unauthenticated-telegram-webhook-request
