# [H] Mattermost allows user with systems manager role with read-only access to teams to perform write operations on teams

## Summary
Severity: High
Advisory: GHSA-fxq9-6946-34q7
CVE: CVE-2024-42497
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2024-08-22
Source: https://github.com/advisories/GHSA-fxq9-6946-34q7
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.5.0 <9.5.8
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.10.0 <9.10.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.9.0 <9.9.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.8.0 <9.8.3

## Details
Mattermost versions 9.9.x <= 9.9.1, 9.5.x <= 9.5.7, 9.10.x <= 9.10.0, 9.8.x <= 9.8.2 fail to properly enforce permissions which allows a user with systems manager role with read-only access to teams to perform write operations on teams.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-42497
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
