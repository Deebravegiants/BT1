# [M] OpenClaw Telegram allowlist authorization accepted mutable usernames

## Summary
Severity: Medium
Advisory: GHSA-mj5r-hh7j-4gxf
CVE: CVE-2026-28480
CWE: CWE-284, CWE-290
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-mj5r-hh7j-4gxf
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14
- npm: `clawdbot` — affected >=0

## Details
## Summary
Telegram allowlist authorization could match on `@username` (mutable/recyclable) instead of immutable numeric sender IDs.

## Impact
Operators who treat Telegram allowlists as strict identity controls could unintentionally grant access if a username changes hands (identity rebinding/spoof risk). This can allow an unauthorized sender to interact with the bot in allowlist mode.

## Affected Packages / Versions
- npm `openclaw`: <= 2026.2.13
- npm `clawdbot`: <= 2026.1.24-3

## Fix
Telegram allowlist authorization now requires numeric Telegram sender IDs only. `@username` allowlist principals are rejected.

A security audit warning was added to flag legacy configs that still contain non-numeric Telegram allowlist entries.

`openclaw doctor --fix` now attempts to resolve `@username` allowFrom entries to numeric IDs (best-effort; requires a Telegram bot token).

## Fix Commit(s)
- e3b432e481a96b8fd41b91273818e514074e05c3
- 9e147f00b48e63e7be6964e0e2a97f2980854128

Thanks @vincentkoc for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-mj5r-hh7j-4gxf
- https://nvd.nist.gov/vuln/detail/CVE-2026-28480
- https://github.com/openclaw/openclaw/commit/9e147f00b48e63e7be6964e0e2a97f2980854128
- https://github.com/openclaw/openclaw/commit/e3b432e481a96b8fd41b91273818e514074e05c3
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
- https://www.vulncheck.com/advisories/openclaw-identity-spoofing-via-mutable-username-in-telegram-allowlist-authorization
