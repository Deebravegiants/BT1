# [M] Mattermost fails to sanitize sensitive data in WebSocket messages

## Summary
Severity: Medium
Advisory: GHSA-pp9j-pf5c-659x
CVE: CVE-2025-13821
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-16
Source: https://github.com/advisories/GHSA-pp9j-pf5c-659x
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20251210191531-cd17b61de41b
- Go: `github.com/mattermost/mattermost-server` — affected >=11.1.0
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0
- Go: `github.com/mattermost/mattermost-server` — affected >=11.2.0
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20251210191531-cd17b61de41b

## Details
Mattermost versions 11.1.x <= 11.1.2, 10.11.x <= 10.11.9, 11.2.x <= 11.2.1 fail to sanitize sensitive data in WebSocket messages which allows authenticated users to exfiltrate password hashes and MFA secrets via profile nickname updates or email verification events. Mattermost Advisory ID: MMSA-2025-00560

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-13821
- https://github.com/mattermost/mattermost/commit/cd17b61de41bf0a49b524bb91ce0bbe859e5a100
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
