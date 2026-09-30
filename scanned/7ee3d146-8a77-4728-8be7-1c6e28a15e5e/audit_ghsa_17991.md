# [M] Mattermost has Potential Server Crash due to Unvalidated Import Data

## Summary
Severity: Medium
Advisory: GHSA-h469-4fcf-p23h
CVE: CVE-2025-8402
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-08-21
Source: https://github.com/advisories/GHSA-h469-4fcf-p23h
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=10.8.0 <10.8.4
- Go: `github.com/mattermost/mattermost-server` — affected >=10.5.0 <10.5.9
- Go: `github.com/mattermost/mattermost-server` — affected >=10.9.0 <10.9.4
- Go: `github.com/mattermost/mattermost-server` — affected >=10.10.0 <10.10.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250708173752-d6b35c41f0ae5
- Go: `github.com/mattermost/mattermost-server` — affected >=9.11.0 <9.11.18
- Go: `github.com/mattermost/mattermost-server/v5` — affected >=0
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0

## Details
Mattermost versions 10.8.x <= 10.8.3, 10.5.x <= 10.5.8, 9.11.x <= 9.11.17, 10.10.x <= 10.10.0, 10.9.x <= 10.9.3 fail to validate import data which allows a system admin to crash the server via the bulk import feature.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-8402
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2025-3911
