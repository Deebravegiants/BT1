# [M] Mattermost Fails to Restrict Certain Operations on System Admins

## Summary
Severity: Medium
Advisory: GHSA-322v-vh2g-qvpv
CVE: CVE-2025-32093
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-04-14
Source: https://github.com/advisories/GHSA-322v-vh2g-qvpv
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=10.5.0 <10.5.2
- Go: `github.com/mattermost/mattermost-server` — affected >=10.4.0 <10.4.4
- Go: `github.com/mattermost/mattermost-server` — affected >=9.11.0 <9.11.10
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.5.0 <10.5.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.4.0 <10.4.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.11.0 <9.11.10
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250227102013-aa4623a93199

## Details
Mattermost versions 10.5.x <= 10.5.1, 10.4.x <= 10.4.3, 9.11.x <= 9.11.9 fail to restrict certain operations on system admins to only other system admins, which allows delegated granular administration users with the "Edit Other Users" permission to perform unauthorized modifications to system administrators via improper permission validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-32093
- https://github.com/mattermost/mattermost/commit/aa4623a9319943d9f54383b22b55e7d06a324e20
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2025-3609
