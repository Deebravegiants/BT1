# [C] Mattermost Server exposes OAuth personal access tokens to attackers

## Summary
Severity: Critical
Advisory: GHSA-876j-jfqf-m7j7
CVE: CVE-2017-18884
CWE: CWE-269, CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-876j-jfqf-m7j7
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.1.2
- Go: `github.com/mattermost/mattermost-server` — affected >=4.2.0-rc1 <4.2.1
- Go: `github.com/mattermost/mattermost-server` — affected >=4.3.0-rc1 <4.3.0

## Details
An issue was discovered in Mattermost Server before 4.3.0, 4.2.1, and 4.1.2. It allows attackers to gain privileges by using a registered OAuth application with personal access tokens.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18884
- https://mattermost.com/security-updates
