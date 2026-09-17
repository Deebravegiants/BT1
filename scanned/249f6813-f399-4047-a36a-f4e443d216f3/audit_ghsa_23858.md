# [H] Mattermost Server does not properly restrict use of slash commands

## Summary
Severity: High
Advisory: GHSA-wvjg-33p9-938h
CVE: CVE-2017-18886
CWE: CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-wvjg-33p9-938h
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.1.2
- Go: `github.com/mattermost/mattermost-server` — affected >=4.2.0-rc1 <4.2.1
- Go: `github.com/mattermost/mattermost-server` — affected >=4.3.0-rc1 <4.3.0

## Details
An issue was discovered in Mattermost Server before 4.3.0, 4.2.1, and 4.1.2. It allows a bypass of restrictions on use of slash commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18886
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
