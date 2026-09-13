# [M] Mattermost crashes web clients via a malformed custom status

## Summary
Severity: Medium
Advisory: GHSA-8f99-g2pj-x8w3
CVE: CVE-2024-4182
CWE: CWE-754
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-04-26
Source: https://github.com/advisories/GHSA-8f99-g2pj-x8w3
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=8.1.0 <8.1.12
- Go: `github.com/mattermost/mattermost-server` — affected >=9.4.0 <9.4.5
- Go: `github.com/mattermost/mattermost-server` — affected >=9.5.0 <9.5.3
- Go: `github.com/mattermost/mattermost-server` — affected >=9.6.0-rc1 <9.6.1

## Details
Mattermost versions 9.6.0, 9.5.x before 9.5.3, 9.4.x before 9.4.5, and 8.1.x before 8.1.12 fail to handle JSON parsing errors in custom status values, which allows an authenticated attacker to crash other users' web clients via a malformed custom status.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-4182
- https://github.com/mattermost/mattermost/commit/41333a0babf565453d89287549bec1e546e75ce7
- https://github.com/mattermost/mattermost/commit/6cbab0f7ece104681f73dd12c75d9f22d567125e
- https://github.com/mattermost/mattermost/commit/a99dadd80c57d376185ca06f8f70919a6f135bc6
- https://github.com/mattermost/mattermost/commit/f84f8ed65f6a5faba974426424b684635455a527
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
