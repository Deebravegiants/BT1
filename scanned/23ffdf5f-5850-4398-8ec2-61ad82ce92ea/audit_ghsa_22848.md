# [M] Mattermost Server is vulnerable to DoS through maliciously crafted posts

## Summary
Severity: Medium
Advisory: GHSA-9589-mq83-f749
CVE: CVE-2017-18898
CWE: CWE-404
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9589-mq83-f749
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.0.5
- Go: `github.com/mattermost/mattermost-server` — affected >=4.1.0 <4.1.1
- Go: `github.com/mattermost/mattermost-server` — affected >=4.2.0-rc1 <4.2.0

## Details
An issue was discovered in Mattermost Server before 4.2.0, 4.1.1, and 4.0.5. It allows crafted posts that potentially cause a web browser to hang.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18898
- https://github.com/grundleborg/mattermost/commit/5286318c72aa230f33f89df3b4cbdc33a0822a93
- https://github.com/mattermost/mattermost/commit/5bf6f06c02c368b9c73a8be2d2d8795b3405b22b
- https://github.com/mattermost/mattermost/commit/5c22176c963a7393241872073547f30083efe218
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
