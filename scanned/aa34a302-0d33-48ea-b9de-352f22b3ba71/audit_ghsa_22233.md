# [M] Mattermost Server exposes sensitive information via its System Console UI

## Summary
Severity: Medium
Advisory: GHSA-9w4v-9c99-hv7r
CVE: CVE-2016-11078
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9w4v-9c99-hv7r
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <3.0.0

## Details
An issue was discovered in Mattermost Server before 3.0.0. It potentially allows attackers to obtain sensitive information (credential fields within config.json) via the System Console UI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-11078
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
