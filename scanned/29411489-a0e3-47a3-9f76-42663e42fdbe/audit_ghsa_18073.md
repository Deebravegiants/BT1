# [M] Mattermost Does Not Sanitize the Team Invite ID

## Summary
Severity: Medium
Advisory: GHSA-qj47-w9f2-qg44
CVE: CVE-2025-47870
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-08-21
Source: https://github.com/advisories/GHSA-qj47-w9f2-qg44
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=10.8.0 <10.8.4
- Go: `github.com/mattermost/mattermost-server` — affected >=10.5.0 <10.5.9
- Go: `github.com/mattermost/mattermost-server` — affected >=9.11.0 <9.11.18
- Go: `github.com/mattermost/mattermost-server` — affected >=10.9.0 <10.9.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250708065844-b38e2eccda18
- Go: `github.com/mattermost/mattermost-server/v5` — affected >=0
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0

## Details
Mattermost versions 10.8.x <= 10.8.3, 10.5.x <= 10.5.8, 9.11.x <= 9.11.17, 10.9.x <= 10.9.2 fail to sanitize the team invite ID in the  POST /api/v4/teams/:teamId/restore endpoint which allows an team admin with no member invite privileges to get the team’s invite id.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-47870
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2025-3905
