# [M] Mattermost's detailed error messages reveal the full file path

## Summary
Severity: Medium
Advisory: GHSA-vx97-8q8q-qgq5
CVE: CVE-2024-32046
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-04-26
Source: https://github.com/advisories/GHSA-vx97-8q8q-qgq5
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=8.1.0 <8.1.12
- Go: `github.com/mattermost/mattermost-server` — affected >=9.5.0 <9.5.3
- Go: `github.com/mattermost/mattermost-server` — affected >=9.6.0-rc1 <9.6.1
- Go: `github.com/mattermost/mattermost-server` — affected >=9.4.0 <9.4.5

## Details
Mattermost versions 9.6.x <= 9.6.0, 9.5.x <= 9.5.2, 9.4.x <= 9.4.4 and 8.1.x <= 8.1.11 fail to remove detailed error messages in API requests even if the developer mode is off which allows an attacker to get information about the server such as the full path were files are stored

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-32046
- https://github.com/mattermost/mattermost/commit/2a48b5b3428cae494452125401e4f72780543ac8
- https://github.com/mattermost/mattermost/commit/93738756ff79777c6e340c8de63a7b4b0f881d27
- https://github.com/mattermost/mattermost/commit/aa222c66b799c12e32eeb8eae6f555bf6140375b
- https://github.com/mattermost/mattermost/commit/c84c25b20c8b8726a2f126ae9370a72498096172
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
