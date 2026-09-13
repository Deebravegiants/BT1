# [M] Mattermost doesn't archive the channel before removing persistent notifications

## Summary
Severity: Medium
Advisory: GHSA-pg7c-462j-grxv
CVE: CVE-2026-4635
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-pg7c-462j-grxv
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=11.6.0 <11.6.1
- Go: `github.com/mattermost/mattermost-server` — affected >=11.5.0 <11.5.4
- Go: `github.com/mattermost/mattermost-server` — affected >=11.4.0 <11.4.5
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.15

## Details
Mattermost versions 11.6.x <= 11.6.0, 11.5.x <= 11.5.3, 11.4.x <= 11.4.4, 10.11.x <= 10.11.14 fail to archive the channel before removing persistent notifications which allows authenticated user to crash the server via timing the creation of persistent notification message between the server deleting existing persistent notifications and archiving the channel. Mattermost Advisory ID: MMSA-2026-00637.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4635
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
