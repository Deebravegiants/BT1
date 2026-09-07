# [H] Mattermost fails to authenticate the source of certain types of post actions

## Summary
Severity: High
Advisory: GHSA-wp43-vprh-c3w5
CVE: CVE-2024-2447
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-04-05
Source: https://github.com/advisories/GHSA-wp43-vprh-c3w5
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.1.0 <8.1.11
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.5.0 <9.5.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.4.0 <9.4.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.3.0 <9.3.3

## Details
Mattermost versions 8.1.x before 8.1.11, 9.3.x before 9.3.3, 9.4.x before 9.4.4, and 9.5.x before 9.5.2 fail to authenticate the source of certain types of post actions, allowing an authenticated attacker to create posts as other users via a crafted post action.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-2447
- https://mattermost.com/security-updates
- mattermost/mattermost
