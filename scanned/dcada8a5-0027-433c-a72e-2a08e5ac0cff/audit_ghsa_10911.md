# [H] Pocket ID: OAuth redirect_uri validation bypass via userinfo/host confusion

## Summary
Severity: High
Advisory: GHSA-9h33-g3ww-mqff
CVE: CVE-2026-28512
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-9h33-g3ww-mqff
Type: github-advisory

## Affected
- Go: `github.com/pocket-id/pocket-id/backend` — affected >=0 <0.0.0-20260228130835-3a339e33191c

## Details
### Impact
A flaw in callback URL validation allowed crafted `redirect_uri` values containing URL userinfo (`@`) to bypass legitimate callback pattern checks. If an attacker can trick a user into opening a malicious authorization link, the authorization code may be redirected to an attacker-controlled host.

### Patches
Fixed in `v2.3.1` (commit 3a339e33191c31b68bf57db907f800d9de5ffbc8).
The fix replaces delimiter-based callback matching with structured URL pattern matching and updates validation logic/tests.

### Workarounds
- Reject callback URLs containing userinfo (`@`) at reverse proxy / app policy level if feasible.

## References
- https://github.com/pocket-id/pocket-id/security/advisories/GHSA-9h33-g3ww-mqff
- https://nvd.nist.gov/vuln/detail/CVE-2026-28512
- https://github.com/pocket-id/pocket-id/commit/3a339e33191c31b68bf57db907f800d9de5ffbc8
- https://github.com/pocket-id/pocket-id
