# [M] Mattermost Fails to Restrict Bookmark Creation and Updates in Archived Channels

## Summary
Severity: Medium
Advisory: GHSA-rp74-x43m-cpw3
CVE: CVE-2025-24920
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-03-21
Source: https://github.com/advisories/GHSA-rp74-x43m-cpw3
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.4.0 <10.4.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.3.0 <10.3.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.11.0 <9.11.9
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.5.0 <10.5.1

## Details
Mattermost versions 10.4.x <= 10.4.2, 10.3.x <= 10.3.3, 9.11.x <= 9.11.8, 10.5.x <= 10.5.0 fail to restrict bookmark creation and updates in archived channels, which allows authenticated users created or update bookmarked in archived channels

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-24920
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
