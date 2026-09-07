# [M] Mattermost Server exposes team invite IDs through API endpoints

## Summary
Severity: Medium
Advisory: GHSA-jwfv-5hwq-f97r
CVE: CVE-2017-18902
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jwfv-5hwq-f97r
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <3.10.3
- Go: `github.com/mattermost/mattermost-server` — affected >=4.0.0 <4.0.4
- Go: `github.com/mattermost/mattermost-server` — affected >=4.0.5-rc1 <4.1.0

## Details
An issue was discovered in Mattermost Server before 4.1.0, 4.0.4, and 3.10.3. It allows attackers to discover team invite IDs via team API endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18902
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
