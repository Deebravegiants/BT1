# [M] Mattermost Server mishandles redirect denial action

## Summary
Severity: Medium
Advisory: GHSA-f7c3-7vp3-44p6
CVE: CVE-2017-18897
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-f7c3-7vp3-44p6
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.0.5
- Go: `github.com/mattermost/mattermost-server` — affected >=4.1.0 <4.1.1
- Go: `github.com/mattermost/mattermost-server` — affected >=4.2.0-rc1 <4.2.0

## Details
An issue was discovered in Mattermost Server before 4.2.0, 4.1.1, and 4.0.5, when used as an OAuth 2.0 service provider. It mishandles a deny action for a redirection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18897
- https://github.com/mattermost/mattermost/commit/3c34e2b2dcb0fde96a10e68d877aa7d0ab511669
- https://github.com/mattermost/mattermost/commit/722fb1947a2e7395ccf16adce9206736d803a9f3
- https://github.com/mattermost/mattermost/commit/d38328976e2c8bb0fab91e656042a0d8ac37bc76
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
