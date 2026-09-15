# [M] Mattermost allows remote actor to set arbitrary RemoteId values for synced users

## Summary
Severity: Medium
Advisory: GHSA-9fpw-c9x7-cv3j
CVE: CVE-2024-41926
CWE: CWE-284, CWE-346
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-08-01
Source: https://github.com/advisories/GHSA-9fpw-c9x7-cv3j
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.5.0 <9.5.7
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.9.0 <9.9.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20240604093018-5114c3b7cdb8
- Go: `github.com/mattermost/mattermost` — affected >=0 <5.3.2-0.20240604093018-5114c3b7cdb8

## Details
Mattermost versions 9.9.x <= 9.9.0 and 9.5.x <= 9.5.6 fail to validate the source of sync messages and only allow the correct remote IDs, which allows a malicious remote to set arbitrary RemoteId values for synced users and therefore claim that a user was synced from another remote.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41926
- https://github.com/mattermost/mattermost/commit/5114c3b7cdb84086959bf0ef8bc5afdaedf9fef6
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2024-3022
