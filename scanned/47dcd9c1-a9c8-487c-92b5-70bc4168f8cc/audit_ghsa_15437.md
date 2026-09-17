# [M] Mattermost allows a user on a remote to set their remote username prop to an arbitrary string

## Summary
Severity: Medium
Advisory: GHSA-vg6q-84p8-qvqh
CVE: CVE-2024-39839
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-08-01
Source: https://github.com/advisories/GHSA-vg6q-84p8-qvqh
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.5.0 <9.5.7
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.7.0 <9.7.6
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.8.0 <9.8.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.9.0 <9.9.1

## Details
Mattermost versions 9.9.x <= 9.9.0, 9.5.x <= 9.5.6, 9.7.x <= 9.7.5, 9.8.x <= 9.8.1 fail to disallow users to set their own remote username, when shared channels were enabled, which allows a user on a remote to set their remote username prop to an arbitrary string, which would be then synced to the local server as long as the user hadn't been synced before.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39839
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2024-3024
