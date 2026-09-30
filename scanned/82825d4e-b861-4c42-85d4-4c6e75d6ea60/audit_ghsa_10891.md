# [M] Mattermost fails to use consistent error responses when handling the /mute command

## Summary
Severity: Medium
Advisory: GHSA-5mr9-crcg-8wh2
CVE: CVE-2026-21386
CWE: CWE-203
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-5mr9-crcg-8wh2
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260130144323-5bb5261c72fa
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20260130144323-5bb5261c72fa
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0-rc1 <10.11.11
- Go: `github.com/mattermost/mattermost-server` — affected >=11.2.0-rc1 <11.2.3
- Go: `github.com/mattermost/mattermost-server` — affected >=11.3.0-rc1 <11.3.1

## Details
Mattermost versions 11.3.x <= 11.3.0, 11.2.x <= 11.2.2, 10.11.x <= 10.11.10 fail to use consistent error responses when handling the /mute command which allows an authenticated team member to enumerate private channels they are not authorized to know about via differing error messages for nonexistent versus private channels. Mattermost Advisory ID: MMSA-2026-00588

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-21386
- https://github.com/mattermost/mattermost/commit/5bb5261c72faa476558a694c23581d24b734da41
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
