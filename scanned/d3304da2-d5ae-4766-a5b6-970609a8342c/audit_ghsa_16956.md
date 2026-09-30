# [M] Mattermost Server doesn't limit the number of user preferences

## Summary
Severity: Medium
Advisory: GHSA-mcw6-3256-64gg
CVE: CVE-2024-28949
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-04-05
Source: https://github.com/advisories/GHSA-mcw6-3256-64gg
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.1.0 <8.1.11
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.3.0 <9.3.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.4.0 <9.4.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.5.0 <9.5.2

## Details
Mattermost Server versions 9.5.x before 9.5.2, 9.4.x before 9.4.4, 9.3.x before 9.3.3, 8.1.x before 8.1.11 don't limit the number of user preferences which allows an attacker to send a large number of user preferences potentially causing denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28949
- https://github.com/mattermost/mattermost/commit/11a21f4da352a472a09de3b8e125514750a6619a
- https://github.com/mattermost/mattermost/commit/362b7d29d35c00fe80721d3d47442a4f3168eb2b
- https://github.com/mattermost/mattermost/commit/5632d6b4ff6d019a21bb8ddd037d4a931cd85ae2
- https://github.com/mattermost/mattermost/commit/88f9285173dc4cb35fa19a8b8604e098a567f704
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2024-2695
- mattermost/mattermost
