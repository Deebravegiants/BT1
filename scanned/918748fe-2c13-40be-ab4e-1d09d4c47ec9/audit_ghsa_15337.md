# [M] Mattermost allows a remote actor to make an arbitrary local channel read-only

## Summary
Severity: Medium
Advisory: GHSA-jr9x-3x7m-4j75
CVE: CVE-2024-41162
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2024-08-01
Source: https://github.com/advisories/GHSA-jr9x-3x7m-4j75
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.5.0 <9.5.7
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.7.0 <9.7.6
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.8.0 <9.8.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.9.0 <9.9.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20240628125750-70b218839fa7
- Go: `github.com/mattermost/mattermost` — affected >=0 <5.3.2-0.20240628125750-70b218839fa7

## Details
Mattermost versions 9.9.x <= 9.9.0, 9.5.x <= 9.5.6, 9.7.x <= 9.7.5 and 9.8.x <= 9.8.1 fail to disallow the modification of local channels by a remote, when shared channels are enabled, which allows a malicious remote to make an arbitrary local channel read-only.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41162
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2024-3031
