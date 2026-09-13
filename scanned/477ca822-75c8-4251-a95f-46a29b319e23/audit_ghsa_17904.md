# [M] Mattermost Fails to Sanitize File Names

## Summary
Severity: Medium
Advisory: GHSA-pj6f-rc94-gw53
CVE: CVE-2025-6465
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-08-21
Source: https://github.com/advisories/GHSA-pj6f-rc94-gw53
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=10.8.0 <10.8.4
- Go: `github.com/mattermost/mattermost-server` — affected >=10.5.0 <10.5.9
- Go: `github.com/mattermost/mattermost-server` — affected >=10.9.0 <10.9.4
- Go: `github.com/mattermost/mattermost-server` — affected >=10.10.0 <10.10.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250708173752-d6b35c41f0ae5

## Details
Mattermost versions 10.8.x <= 10.8.3, 10.5.x <= 10.5.8, 10.10.x <= 10.10.0, 10.9.x <= 10.9.3 fail to sanitize file names which allows users with file upload permission to overwrite file attachment thumbnails via path traversal in file streaming APIs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6465
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2025-3906
