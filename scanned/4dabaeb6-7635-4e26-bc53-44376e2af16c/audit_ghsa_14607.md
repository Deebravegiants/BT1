# [M] Mattermost Race Condition vulnerability

## Summary
Severity: Medium
Advisory: GHSA-826h-p4c3-477p
CVE: CVE-2024-48872
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-12-16
Source: https://github.com/advisories/GHSA-826h-p4c3-477p
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.1.0 <10.1.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.0.0 <10.0.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.11.0 <9.11.5
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.5.0 <9.5.13

## Details
Mattermost versions 10.1.x <= 10.1.2, 10.0.x <= 10.0.2, 9.11.x <= 9.11.4, and 9.5.x <= 9.5.12 fail to prevent concurrently checking and updating the failed login attempts. which allows an attacker to bypass of "Max failed attempts" restriction and send a big number of login attempts before being blocked via simultaneously sending multiple login requests

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-48872
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
