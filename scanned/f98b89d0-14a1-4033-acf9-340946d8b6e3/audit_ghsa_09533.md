# [M] Mattermost doesn't sanitize team member data when returned via API to users without elevated permissions

## Summary
Severity: Medium
Advisory: GHSA-ffpr-pfr4-g354
CVE: CVE-2026-3636
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-ffpr-pfr4-g354
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=11.6.0 <11.6.1
- Go: `github.com/mattermost/mattermost-server` — affected >=11.5.0 <11.5.4
- Go: `github.com/mattermost/mattermost-server` — affected >=11.4.0 <11.4.5
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.15

## Details
Mattermost versions 11.6.x <= 11.6.0, 11.5.x <= 11.5.3, 11.4.x <= 11.4.4, 10.11.x <= 10.11.14 fail to sanitize team member data when returned via API to users without elevated permissions which allows a user without permissions to get data about team members roles via invoking various team API endpoints. Mattermost Advisory ID: MMSA-2026-00626.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3636
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
