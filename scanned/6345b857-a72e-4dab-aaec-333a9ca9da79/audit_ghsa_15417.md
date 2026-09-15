# [M] Mattermost failed to disallow the modification of local users when syncing users in shared channels

## Summary
Severity: Medium
Advisory: GHSA-56mc-f9w7-2wxq
CVE: CVE-2024-36492
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-08-01
Source: https://github.com/advisories/GHSA-56mc-f9w7-2wxq
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.5.0 <9.5.7
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.7.0 <9.7.6
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.8.0 <9.8.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.9.0 <9.9.1

## Details
Mattermost versions 9.9.x <= 9.9.0, 9.5.x <= 9.5.6, 9.7.x <= 9.7.5, 9.8.x <= 9.8.1 fail to disallow the modification of local users when syncing users in shared channels. which allows a malicious remote to overwrite an existing local user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36492
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2024-3025
