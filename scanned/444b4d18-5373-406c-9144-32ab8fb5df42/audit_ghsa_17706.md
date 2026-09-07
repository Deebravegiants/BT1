# [M] Mattermost fails to properly validate post props

## Summary
Severity: Medium
Advisory: GHSA-45v9-w9fh-33j6
CVE: CVE-2025-20088
CWE: CWE-1287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-01-15
Source: https://github.com/advisories/GHSA-45v9-w9fh-33j6
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.2.0 <10.2.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.1.0 <10.1.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.0.0 <10.0.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.11.0 <9.11.6
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20241127161322-25ff7a3779a5

## Details
Mattermost versions 10.2.x <= 10.2.0, 9.11.x <= 9.11.5, 10.0.x <= 10.0.3, 10.1.x <= 10.1.3 fail to properly validate post props which allows a malicious authenticated user to cause a crash via a malicious post.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-20088
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2025-3394
