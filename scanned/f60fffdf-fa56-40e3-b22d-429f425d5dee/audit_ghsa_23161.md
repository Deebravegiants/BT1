# [M] Mattermost Server exposes sensitive user status information via REST API version 4 endpoint

## Summary
Severity: Medium
Advisory: GHSA-h742-xx59-r9pq
CVE: CVE-2017-18895
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h742-xx59-r9pq
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.0.5
- Go: `github.com/mattermost/mattermost-server` — affected >=4.1.0 <4.1.1
- Go: `github.com/mattermost/mattermost-server` — affected >=4.2.0-rc1 <4.2.0

## Details
An issue was discovered in Mattermost Server before 4.2.0, 4.1.1, and 4.0.5. It allows attackers to obtain sensitive information (user statuses) via a REST API version 4 endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18895
- https://github.com/mattermost/mattermost/commit/3c34e2b2dcb0fde96a10e68d877aa7d0ab511669
- https://github.com/mattermost/mattermost/commit/722fb1947a2e7395ccf16adce9206736d803a9f3
- https://github.com/mattermost/mattermost/commit/d38328976e2c8bb0fab91e656042a0d8ac37bc76
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
