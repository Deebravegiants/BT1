# [M] Mattermost Fails to Validate Team Invite Permissions

## Summary
Severity: Medium
Advisory: GHSA-r7r2-m3vr-c8qc
CVE: CVE-2025-3446
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-05-15
Source: https://github.com/advisories/GHSA-r7r2-m3vr-c8qc
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.6.0 <10.6.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.5.0 <10.5.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.4.0 <10.4.5
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.11.0 <9.11.12
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250415054241-76ab3867b785

## Details
Mattermost versions 10.6.x <= 10.6.1, 10.5.x <= 10.5.2, 10.4.x <= 10.4.4, 9.11.x <= 9.11.11 fail to check the correct permissions which allows authenticated users who only have permission to invite non-guest users to a team to add guest users to that team via the API to add a single user to a team.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3446
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
