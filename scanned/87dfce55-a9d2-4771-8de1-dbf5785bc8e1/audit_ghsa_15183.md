# [M] Mattermost viewing archived public channels permissions vulnerability

## Summary
Severity: Medium
Advisory: GHSA-w88v-pjr8-cmv2
CVE: CVE-2023-47858
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-01-02
Source: https://github.com/advisories/GHSA-w88v-pjr8-cmv2
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0 <7.8.10
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.1.1

## Details
Mattermost fails to properly verify the permissions needed for viewing archived public channels,  allowing a member of one team to get details about the archived public channels of another team via the GET /api/v4/teams/<team-id>/channels/deleted endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-47858
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
