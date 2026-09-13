# [M] Mattermost fails to limit the number of role names

## Summary
Severity: Medium
Advisory: GHSA-vm9m-57jr-4pxh
CVE: CVE-2024-1953
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-02-29
Source: https://github.com/advisories/GHSA-vm9m-57jr-4pxh
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.4.0 <9.4.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.3.0 <9.3.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.2.0 <9.2.5
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.1.9

## Details
Mattermost versions 8.1.x before 8.1.9, 9.2.x before 9.2.5, 9.3.0, and 9.4.x before 9.4.2 fail to limit the number of role names requested from the API, allowing an authenticated attacker to cause the server to run out of memory and crash by issuing an unusually large HTTP request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1953
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2024-2594
