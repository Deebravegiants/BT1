# [M] Mattermost Server: Files may be rendered inline instead of downloaded, allowing script execution

## Summary
Severity: Medium
Advisory: GHSA-rm24-25xm-9454
CVE: CVE-2016-11083
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rm24-25xm-9454
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <2.2.0

## Details
An issue was discovered in Mattermost Server before 2.2.0. It allows XSS because it configures files to be opened in a browser window.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-11083
- https://github.com/mattermost/mattermost/commit/480308b7029a04cf41d0e9e7cd68b52dc2138e98
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
