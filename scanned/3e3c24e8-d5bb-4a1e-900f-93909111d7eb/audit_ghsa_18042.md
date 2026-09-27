# [M] Mattermost Fails to Validate File Paths

## Summary
Severity: Medium
Advisory: GHSA-gq3r-5833-5532
CVE: CVE-2025-36530
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-08-21
Source: https://github.com/advisories/GHSA-gq3r-5833-5532
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=10.9.0 <10.9.2
- Go: `github.com/mattermost/mattermost-server` — affected >=10.8.0 <10.8.4
- Go: `github.com/mattermost/mattermost-server` — affected >=10.5.0 <10.5.9
- Go: `github.com/mattermost/mattermost-server` — affected >=9.11.0 <9.11.18
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250619095651-9dd0b3943e55
- Go: `github.com/mattermost/mattermost-server/v5` — affected >=0
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0

## Details
Mattermost versions 10.9.x <= 10.9.1, 10.8.x <= 10.8.3, 10.5.x <= 10.5.8, 9.11.x <= 9.11.17 fail to properly validate file paths during plugin import operations which allows restricted admin users to install unauthorized custom plugins via path traversal in the import functionality, bypassing plugin signature enforcement and marketplace restrictions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-36530
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2025-3901
