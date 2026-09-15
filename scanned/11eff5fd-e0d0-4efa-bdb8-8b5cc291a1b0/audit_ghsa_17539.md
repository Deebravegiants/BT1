# [M] Mattermost allows unauthorized channel member management through playbook runs

## Summary
Severity: Medium
Advisory: GHSA-qwwm-c582-82rx
CVE: CVE-2025-3227
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-06-20
Source: https://github.com/advisories/GHSA-qwwm-c582-82rx
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <0.0.0-20250520060012-d0380305ef7a
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250520060012-d0380305ef7a
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.5.0 <10.5.6
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.11.0 <9.11.16
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.8.0 <10.8.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.7.0 <10.7.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.6.0 <10.6.6

## Details
Mattermost versions 10.5.x <= 10.5.5, 9.11.x <= 9.11.15, 10.8.x <= 10.8.0, 10.7.x <= 10.7.2, 10.6.x <= 10.6.5 fail to properly enforce channel member management permissions in playbook runs, allowing authenticated users without the 'Manage Channel Members' permission to add or remove users from public and private channels by manipulating playbook run participants when the run is linked to a channel.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3227
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
