# [H] Mattermost Server: initial_load API exposes unnecessary information

## Summary
Severity: High
Advisory: GHSA-r93j-3mmp-px57
CVE: CVE-2016-11066
CWE: CWE-200, CWE-359
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-r93j-3mmp-px57
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <3.1.1

## Details
An issue was discovered in Mattermost Server before 3.1.1. The initial_load API disclosed unnecessary personal information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-11066
- https://github.com/mattermost/mattermost/commit/f89e7c6d543a82d6078c2ca0f892914d7976a6f5
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
