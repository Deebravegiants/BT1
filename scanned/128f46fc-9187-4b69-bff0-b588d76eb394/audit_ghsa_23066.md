# [M] Mattermost Server is vulnerable to XSS attacks against an OAuth 2.0 allow/deny page

## Summary
Severity: Medium
Advisory: GHSA-9x8x-w6g5-hx4w
CVE: CVE-2017-18877
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9x8x-w6g5-hx4w
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.1.2
- Go: `github.com/mattermost/mattermost-server` — affected >=4.2.0 <4.2.1
- Go: `github.com/mattermost/mattermost-server` — affected >=4.3.0-rc1 <4.3.0

## Details
An issue was discovered in Mattermost Server before 4.3.0, 4.2.1, and 4.1.2. XSS attacks could occur against an OAuth 2.0 allow/deny page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18877
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
