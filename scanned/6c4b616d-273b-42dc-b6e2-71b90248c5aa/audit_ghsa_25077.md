# [M] Mattermost Server is vulnerable to XSS through lack of link relationship attributes `noreferrer` and `noopener`

## Summary
Severity: Medium
Advisory: GHSA-h3qg-w9j5-wh3m
CVE: CVE-2016-11071
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h3qg-w9j5-wh3m
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <3.1.0

## Details
An issue was discovered in Mattermost Server before 3.1.0. It allows XSS because the noreferrer and noopener protection mechanisms were not in place.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-11071
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
