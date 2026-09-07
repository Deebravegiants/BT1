# [H] Mattermost Server has intermittent Authorization bypass for resource-owners

## Summary
Severity: High
Advisory: GHSA-gg42-mwr6-p82c
CVE: CVE-2017-18894
CWE: CWE-639, CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-gg42-mwr6-p82c
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.0.5
- Go: `github.com/mattermost/mattermost-server` — affected >=4.1.0 <4.1.1
- Go: `github.com/mattermost/mattermost-server` — affected >=4.2.0-rc1 <4.2.0

## Details
An issue was discovered in Mattermost Server before 4.2.0, 4.1.1, and 4.0.5, when used as an OAuth 2.0 service provider. Resource-owner authorization can be intermittently bypassed, allowing account takeover.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18894
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
