# [H] Mattermost Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-7664-hcp7-f497
CVE: CVE-2023-6458
CWE: CWE-22, CWE-74
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2023-12-06
Source: https://github.com/advisories/GHSA-7664-hcp7-f497
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0 <7.8.14
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.1.5
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.0.0 <9.0.3
- Go: `github.com/mattermost/mattermost/server` — affected >=9.1.0 <9.1.2

## Details
Mattermost webapp fails to validate route parameters in/<TEAM_NAME>/channels/<CHANNEL_NAME> allowing an attacker to perform a client-side path traversal.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6458
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
