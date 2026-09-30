# [M] Mattermost fails to validate user permissions when deleting comments in Boards

## Summary
Severity: Medium
Advisory: GHSA-p6gj-jc38-x2m7
CVE: CVE-2025-12756
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-12-01
Source: https://github.com/advisories/GHSA-p6gj-jc38-x2m7
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0
- Go: `github.com/mattermost/mattermost` — affected >=10.11.0
- Go: `github.com/mattermost/mattermost` — affected >=10.12.0
- Go: `github.com/mattermost/mattermost` — affected >=10.5.0
- Go: `github.com/mattermost/mattermost` — affected >=11.0.0

## Details
Mattermost versions 11.0.x <= 11.0.2, 10.12.x <= 10.12.1, 10.11.x <= 10.11.4, 10.5.x <= 10.5.12 fail to validate user permissions when deleting comments in Boards, which allows an authenticated user with the editor role to delete comments created by other users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12756
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
