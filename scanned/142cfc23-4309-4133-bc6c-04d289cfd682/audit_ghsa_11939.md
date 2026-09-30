# [M] OpenClaw's Nextcloud Talk webhook replay could trigger duplicate inbound processing

## Summary
Severity: Medium
Advisory: GHSA-r9q5-c7qc-p26w
CVE: CVE-2026-28449
CWE: CWE-294
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-r9q5-c7qc-p26w
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.25

## Details
### Summary
When Nextcloud Talk webhook signing was valid, replayed requests could be accepted without durable replay suppression, allowing duplicate inbound processing after replay-window expiry or process restart.

### Details
OpenClaw's Nextcloud Talk webhook path verified `HMAC(secret, random + body)` but previously lacked durable replay state tied to webhook events. This allowed replay of a previously valid signed request in some operational conditions.

The fix on `main` adds:
- persistent per-account replay dedupe for Nextcloud Talk webhook events,
- replay checks before webhook side effects (`onMessage`),
- backend-origin validation against configured account base URL (when configured).

### Impact
A captured valid signed webhook request could be replayed to trigger duplicate inbound handling. This is an integrity/availability issue (duplicate actions/noise), scoped to deployments using Nextcloud Talk webhook integration.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: `<= 2026.2.24`
- Patched in release: `2026.2.25`

### Fix Commit(s)
- `d512163d686ad6741783e7119ddb3437f493dbbc`

### Release Process Note
`patched_versions` is pre-set to the release (`2026.2.25`) so once npm release `2026.2.25` is published, advisory is now published.

OpenClaw thanks @aristorechina for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-r9q5-c7qc-p26w
- https://nvd.nist.gov/vuln/detail/CVE-2026-28449
- https://github.com/openclaw/openclaw/commit/d512163d686ad6741783e7119ddb3437f493dbbc
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-webhook-replay-attack-via-missing-durable-replay-suppression
