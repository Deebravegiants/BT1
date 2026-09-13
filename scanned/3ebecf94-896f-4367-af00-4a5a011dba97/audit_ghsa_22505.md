# [M] Mattermost Server is vulnerable to Directory Traversal by System Admins

## Summary
Severity: Medium
Advisory: GHSA-8qg8-c7mw-6fj7
CVE: CVE-2017-18874
CWE: CWE-22
Ecosystem: Go
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8qg8-c7mw-6fj7
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.1.2-0.20171004201910-6be8113eb60
- Go: `github.com/mattermost/mattermost-server` — affected >=4.2.0-rc1 <4.2.1-0.20171004194140-6d3cb2ce07fc
- Go: `github.com/mattermost/mattermost-server` — affected >=4.3.0-rc1 <4.3.0

## Details
An issue was discovered in Mattermost Server before 4.3.0, 4.2.1, and 4.1.2 when local storage for files is used. A System Admin can achieve directory traversal.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18874
- https://github.com/mattermost/mattermost/commit/6be8113eb60cf5ddd2dc1c3f4db05cae0c183086
- https://github.com/mattermost/mattermost/commit/6d3cb2ce07fc799832081e93843b405b390057fa
- https://github.com/mattermost/mattermost/commit/fadd9514f6e71590aba781a7035e1de4150137b0
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
