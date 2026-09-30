# [M] Mattermost Fails to Validate Remote Cluster Upload Sessions

## Summary
Severity: Medium
Advisory: GHSA-q453-638c-h4mr
CVE: CVE-2025-49222
CWE: CWE-434
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-08-21
Source: https://github.com/advisories/GHSA-q453-638c-h4mr
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=10.8.0 <10.8.4
- Go: `github.com/mattermost/mattermost-server` — affected >=10.5.0 <10.5.9
- Go: `github.com/mattermost/mattermost-server` — affected >=9.11.0 <9.11.18
- Go: `github.com/mattermost/mattermost-server` — affected >=10.9.0 <10.9.3
- Go: `github.com/mattermost/mattermost-server` — affected >=10.10.0 <10.10.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250708173752-d6b35c41f0ae5
- Go: `github.com/mattermost/mattermost-server/v5` — affected >=0
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0

## Details
Mattermost versions 10.8.x <= 10.8.3, 10.5.x <= 10.5.8, 9.11.x <= 9.11.17, 10.9.x <= 10.9.2, 10.10.x <= 10.10.0 fail to validate upload types in remote cluster upload sessions which allows a system admin to upload non-attachment file types via shared channels that could potentially be placed in arbitrary filesystem directories.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-49222
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2025-3904
