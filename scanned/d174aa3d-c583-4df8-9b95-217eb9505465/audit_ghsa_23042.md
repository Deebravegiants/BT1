# [C] Mattermost Server allows attackers to gain privileges by accessing unintended API endpoints with users' credentials

## Summary
Severity: Critical
Advisory: GHSA-g78f-6xq7-rrhq
CVE: CVE-2017-18885
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-g78f-6xq7-rrhq
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.1.2
- Go: `github.com/mattermost/mattermost-server` — affected >=4.2.0-rc1 <4.2.1
- Go: `github.com/mattermost/mattermost-server` — affected >=4.3.0-rc1 <4.3.0

## Details
An issue was discovered in Mattermost Server before 4.3.0, 4.2.1, and 4.1.2. It allows attackers to gain privileges by accessing unintended API endpoints on a user's behalf.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18885
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
