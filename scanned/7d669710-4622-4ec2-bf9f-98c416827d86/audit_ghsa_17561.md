# [M] Mattermost allows an unauthorized Guest user access to Playbook

## Summary
Severity: Medium
Advisory: GHSA-4578-6gjh-f2jm
CVE: CVE-2025-3228
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-06-20
Source: https://github.com/advisories/GHSA-4578-6gjh-f2jm
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
Mattermost versions 10.5.x <= 10.5.5, 9.11.x <= 9.11.15, 10.8.x <= 10.8.0, 10.7.x <= 10.7.2, 10.6.x <= 10.6.5 fail to properly retrieve requestorInfo from playbooks handler for guest users which allows an attacker access to the playbook run.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3228
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
