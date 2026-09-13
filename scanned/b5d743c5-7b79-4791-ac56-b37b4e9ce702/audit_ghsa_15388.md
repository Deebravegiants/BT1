# [M] Mattermost doesn't redact remote users' original email addresses

## Summary
Severity: Medium
Advisory: GHSA-4ww8-fprq-cq34
CVE: CVE-2024-32939
CWE: CWE-284, CWE-312
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-08-22
Source: https://github.com/advisories/GHSA-4ww8-fprq-cq34
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.9.0 <9.9.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.5.0 <9.5.8
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.10.0 <9.10.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.8.0 <9.8.3

## Details
Mattermost versions 9.9.x <= 9.9.1, 9.5.x <= 9.5.7, 9.10.x <= 9.10.0, 9.8.x <= 9.8.2, when shared channels are enabled, fail to redact remote users' original email addresses stored in user props when email addresses are otherwise configured not to be visible in the local server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-32939
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
