# [M] Mattermost Uncontrolled Resource Consumption vulnerability

## Summary
Severity: Medium
Advisory: GHSA-33r7-wjfc-7w98
CVE: CVE-2023-5196
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-09-29
Source: https://github.com/advisories/GHSA-33r7-wjfc-7w98
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.1.0 <8.1.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.0.0 <8.0.2
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0 <7.8.10

## Details
Mattermost fails to enforce character limits in all possible notification props allowing an attacker to send a really long value for a notification_prop resulting in the server consuming an abnormal quantity of computing resources and possibly becoming temporarily unavailable for its users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5196
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
