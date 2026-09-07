# [C] Mattermost Server is vulnerable to SQL Injection when executing multiple POST requests

## Summary
Severity: Critical
Advisory: GHSA-v2vm-hq26-5jv6
CVE: CVE-2017-18888
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-v2vm-hq26-5jv6
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.1.2
- Go: `github.com/mattermost/mattermost-server` — affected >=4.2.0-rc1 <4.2.1
- Go: `github.com/mattermost/mattermost-server` — affected >=4.3.0-rc1 <4.3.0

## Details
An issue was discovered in Mattermost Server before 4.3.0, 4.2.1, and 4.1.2. It allows SQL injection during the fetching of multiple posts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18888
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
