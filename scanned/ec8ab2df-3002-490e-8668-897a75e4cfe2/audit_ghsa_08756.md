# [H] Mattermost has a Path Traversal issue

## Summary
Severity: High
Advisory: GHSA-c4r7-j7pp-r8mp
CVE: CVE-2026-4858
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-c4r7-j7pp-r8mp
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=11.6.0 <11.6.1
- Go: `github.com/mattermost/mattermost-server` — affected >=11.5.0 <11.5.4
- Go: `github.com/mattermost/mattermost-server` — affected >=11.4.0 <11.4.5
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.15

## Details
Mattermost versions 11.6.x <= 11.6.0, 11.5.x <= 11.5.3, 11.4.x <= 11.4.4, 10.11.x <= 10.11.14 fail to check integration URL for path traversal which allows an malicious authenticated user  to call an arbitrary API via system admin Mattermost auth token using via path traversal in integration action URL. Mattermost Advisory ID: MMSA-2026-00640.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4858
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
