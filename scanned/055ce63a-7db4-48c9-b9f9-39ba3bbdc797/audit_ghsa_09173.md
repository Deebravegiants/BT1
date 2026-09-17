# [H] Mattermost doesn't validate file ownership and access control

## Summary
Severity: High
Advisory: GHSA-7pf2-9c95-w332
CVE: CVE-2026-3473
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-7pf2-9c95-w332
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=11.6.0 <11.6.1
- Go: `github.com/mattermost/mattermost-server` — affected >=11.5.0 <11.5.4
- Go: `github.com/mattermost/mattermost-server` — affected >=11.4.0 <11.4.5
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.15

## Details
Mattermost versions 11.6.x <= 11.6.0, 11.5.x <= 11.5.3, 11.4.x <= 11.4.4, 10.11.x <= 10.11.14 fail to validate file ownership and access control, which allows an authenticated user to access and download files belonging to other users or teams via crafted Boards API requests using valid file IDs. Mattermost Advisory ID: MMSA-2026-00620.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3473
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
