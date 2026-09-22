# [M] Mattermost Server is vulnerable to webhook and slash command manipulation

## Summary
Severity: Medium
Advisory: GHSA-jp57-4x34-5v94
CVE: CVE-2017-18889
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jp57-4x34-5v94
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.1.2
- Go: `github.com/mattermost/mattermost-server` — affected >=4.2.0-rc1 <4.2.1
- Go: `github.com/mattermost/mattermost-server` — affected >=4.3.0-rc1 <4.3.0

## Details
An issue was discovered in Mattermost Server before 4.3.0, 4.2.1, and 4.1.2. An attacker could create fictive system-message posts via webhooks and slash commands, in the v3 or v4 REST API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18889
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
