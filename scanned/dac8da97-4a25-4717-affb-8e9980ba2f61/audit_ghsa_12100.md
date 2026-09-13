# [M] OpenClaw Telegram media fetch errors exposed bot tokens in logged file URLs

## Summary
Severity: Medium
Advisory: GHSA-xwcj-hwhf-h378
CWE: CWE-532
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-xwcj-hwhf-h378
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.13

## Details
### Summary
`openclaw` versions `<= 2026.3.12` could include raw Telegram bot tokens in media fetch error strings when inbound Telegram media downloads failed.

### Affected Packages / Versions
- Package: `openclaw` (`npm`)
- Affected versions: `<= 2026.3.12`
- Fixed version: `2026.3.13`

### Details
The vulnerable path was `fetchRemoteMedia()` in `src/media/fetch.ts`. In affected releases, fetch and HTTP error paths embedded the original Telegram file URL into `MediaFetchError` messages. For Telegram media, those URLs can include `/file/bot<TOKEN>/...`, so the resulting error strings could leak bot tokens into logs, console output, or any downstream error surface that rendered the exception text.

This issue is in scope under OpenClaw's trust model because the leaked secret is an OpenClaw-operated integration credential, not a user-supplied third-party secret.

### Fix
`openclaw@2026.3.13` redacts sensitive media URLs before constructing fetch error messages. Current code routes the source URL and follow-on error paths through `redactMediaUrl()` / `redactSensitiveText()`, so Telegram bot tokens are no longer emitted in those error strings.

Regression coverage exists in `src/media/fetch.test.ts` (`redacts Telegram bot tokens from fetch failure messages` and `redacts Telegram bot tokens from HTTP error messages`).

### Fix Commit(s)
- `7a53eb7ea8295b08be137e231c9a98c1a79b5cd5`

Thanks @space08 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-xwcj-hwhf-h378
- https://github.com/openclaw/openclaw/commit/7a53eb7ea8295b08be137e231c9a98c1a79b5cd5
- https://github.com/openclaw/openclaw
