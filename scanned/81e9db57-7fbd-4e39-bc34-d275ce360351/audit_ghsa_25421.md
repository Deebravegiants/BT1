# [C] Mattermost Server password reset email requests can be sent to attacker-provided email addresses

## Summary
Severity: Critical
Advisory: GHSA-34cx-hvm4-vx7j
CVE: CVE-2017-18908
CWE: CWE-287, CWE-640
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-34cx-hvm4-vx7j
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <3.9.1-rc1
- Go: `github.com/mattermost/mattermost-server` — affected >=3.10.0 <3.10.1

## Details
An issue was discovered in Mattermost Server before 4.0.0, 3.10.1, and 3.9.1. A password reset request was sometimes sent to an attacker-provided e-mail address.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18908
- https://github.com/mattermost/mattermost/commit/59139390ae927af2e879dbacfe4dadb1adac97c0
- https://github.com/mattermost/mattermost/commit/d3bc11be3acd3a73e6358d958b91427e2584ea71
- https://github.com/mattermost/mattermost/commit/e5065cf7575ee05c040945a4b00b7fd90bf39b83
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
