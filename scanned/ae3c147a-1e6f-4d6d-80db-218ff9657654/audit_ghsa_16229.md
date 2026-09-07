# [M] Mattermost fails to check the "invite_guest" permission 

## Summary
Severity: Medium
Advisory: GHSA-pfw6-5rx3-xh3c
CVE: CVE-2024-1888
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-02-29
Source: https://github.com/advisories/GHSA-pfw6-5rx3-xh3c
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.4.0 <9.4.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.3.0 <9.3.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.2.0 <9.2.5
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.1.9

## Details
Mattermost fails to check the "invite_guest" permission when inviting guests of other teams to a team, allowing a member with permissions to add other members but not to add guests to add a guest to a team as long as the guest was already a guest in another team of the server

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1888
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
