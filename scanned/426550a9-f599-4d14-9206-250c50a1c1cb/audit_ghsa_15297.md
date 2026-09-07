# [M] Mattermost Cross-Site Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hrf9-rm95-fpf3
CVE: CVE-2024-40886
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-08-22
Source: https://github.com/advisories/GHSA-hrf9-rm95-fpf3
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.9.0 <9.9.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.5.0 <9.5.8
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.10.0 <9.10.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.8.0 <9.8.3

## Details
Mattermost versions 9.9.x <= 9.9.1, 9.5.x <= 9.5.7, 9.10.x <= 9.10.0, 9.8.x <= 9.8.2 fail to sanitize user inputs in the frontend that are used for redirection which allows for a one-click client-side path traversal that is leading to CSRF in User Management page of the system console.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-40886
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
