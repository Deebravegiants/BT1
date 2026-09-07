# [M] Mattermost Server exposes information stored by a web browser

## Summary
Severity: Medium
Advisory: GHSA-5q37-9874-qxcw
CVE: CVE-2016-11081
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5q37-9874-qxcw
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <2.2.0

## Details
An issue was discovered in Mattermost Server before 2.2.0. It allows unintended access to information stored by a web browser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-11081
- https://github.com/mattermost/mattermost/commit/a51a8ebc264c89f227e831c01fa048dafb7ee6c6
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
