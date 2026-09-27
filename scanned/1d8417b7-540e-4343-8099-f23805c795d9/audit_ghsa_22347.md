# [M] Mattermost Server allows attackers to create buttons that can launch API requests

## Summary
Severity: Medium
Advisory: GHSA-m497-hq5x-6jcv
CVE: CVE-2017-18890
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m497-hq5x-6jcv
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.1.2
- Go: `github.com/mattermost/mattermost-server` — affected >=4.2.0-rc1 <4.2.1
- Go: `github.com/mattermost/mattermost-server` — affected >=4.3.0-rc1 <4.3.0

## Details
An issue was discovered in Mattermost Server before 4.3.0, 4.2.1, and 4.1.2. It allows an attacker to create a button that, when pressed by a user, launches an API request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18890
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
