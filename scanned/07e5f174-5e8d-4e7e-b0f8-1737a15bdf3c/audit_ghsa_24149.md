# [M] Mattermost Server is vulnerable to Uncontrolled Resource Consumption

## Summary
Severity: Medium
Advisory: GHSA-ffcc-qr2v-3qmv
CVE: CVE-2016-11067
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-ffcc-qr2v-3qmv
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <3.2.0

## Details
An issue was discovered in Mattermost Server before 3.2.0. It allowed crafted posts that could cause a web browser to hang.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-11067
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
