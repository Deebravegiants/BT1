# [M] Mattermost Server exposes team creator's e-mail address to other members

## Summary
Severity: Medium
Advisory: GHSA-35c4-5qfp-wxj6
CVE: CVE-2017-18887
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-35c4-5qfp-wxj6
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.1.2
- Go: `github.com/mattermost/mattermost-server` — affected >=4.2.0-rc1 <4.2.1
- Go: `github.com/mattermost/mattermost-server` — affected >=4.3.0-rc1 <4.3.0

## Details
An issue was discovered in Mattermost Server before 4.3.0, 4.2.1, and 4.1.2. It discloses the team creator's e-mail address to members.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18887
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
