# [M] Mattermost Fails to Sanitize Path Traversal Sequences

## Summary
Severity: Medium
Advisory: GHSA-x67c-v8jr-p29r
CVE: CVE-2025-8023
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-08-21
Source: https://github.com/advisories/GHSA-x67c-v8jr-p29r
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=10.8.0 <10.8.4
- Go: `github.com/mattermost/mattermost-server` — affected >=10.5.0 <10.5.9
- Go: `github.com/mattermost/mattermost-server` — affected >=9.11.0 <9.11.18
- Go: `github.com/mattermost/mattermost-server` — affected >=10.9.0 <10.9.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250708065844-b38e2eccda18
- Go: `github.com/mattermost/mattermost-server/v5` — affected >=0
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0

## Details
Mattermost versions 10.8.x <= 10.8.3, 10.5.x <= 10.5.8, 9.11.x <= 9.11.17, 10.9.x <= 10.9.2 fails to sanitize path traversal sequences in template file destination paths, which allows a system admin to perform path traversal attacks via malicious path components, potentially enabling malicious file placement outside intended directories.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-8023
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2025-3907
