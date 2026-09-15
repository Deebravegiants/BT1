# [M] Mattermost Server has low entropy for authorization data as an OAuth 2.0 Service Provider

## Summary
Severity: Medium
Advisory: GHSA-w8cc-3h7q-jhc3
CVE: CVE-2017-18883
CWE: CWE-331
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-w8cc-3h7q-jhc3
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.1.2
- Go: `github.com/mattermost/mattermost-server` — affected >=4.2.0-rc1 <4.2.1
- Go: `github.com/mattermost/mattermost-server` — affected >=4.3.0-rc1 <4.3.0

## Details
An issue was discovered in Mattermost Server before 4.3.0, 4.2.1, and 4.1.2, when serving as an OAuth 2.0 Service Provider. There is low entropy for authorization data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18883
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
