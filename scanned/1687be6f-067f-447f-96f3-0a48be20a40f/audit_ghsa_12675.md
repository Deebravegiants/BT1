# [M] Mattermost Server Missing Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-455c-vqrf-mghr
CVE: CVE-2023-2783
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-06-16
Source: https://github.com/advisories/GHSA-455c-vqrf-mghr
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=7.10.0 <7.10.1
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=7.9.0 <7.9.4
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=6.0.0 <7.8.5
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0 <6.0.0-20230511130429-1629a6ca7fed

## Details
Mattermost Apps Framework fails to verify that a secret provided in the incoming webhook request allowing an attacker to modify the contents of the post sent by the Apps.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2783
- https://github.com/mattermost/mattermost-server
- https://mattermost.com/security-updates
