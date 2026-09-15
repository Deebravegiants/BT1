# [M] Mattermost Playbooks fails to validate the uniqueness and quantity of task actions

## Summary
Severity: Medium
Advisory: GHSA-689c-xq7x-xjwf
CVE: CVE-2025-35965
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-24
Source: https://github.com/advisories/GHSA-689c-xq7x-xjwf
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250218121836-2b5275d87136
- Go: `github.com/mattermost/mattermost-plugin-playbooks` — affected >=2.0.0
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.4.0
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.5.0
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.11.0
- Go: `github.com/mattermost/mattermost-plugin-playbooks` — affected >=0 <1.41.0

## Details
Mattermost versions 10.4.x <= 10.4.2, 10.5.x <= 10.5.0, 9.11.x <= 9.11.10 fail to validate the uniqueness and quantity of task actions within the UpdateRunTaskActions GraphQL operation, which allows an attacker to create task items containing an excessive number of actions triggered by specific posts, overloading the server and leading to a denial-of-service (DoS) condition.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-35965
- https://github.com/mattermost/mattermost-plugin-playbooks/commit/bf2633dad09f5768ce2bea4b7c5ffb74050052a8
- https://github.com/mattermost/mattermost/commit/2b5275d87136f07e016c8eca09a2f004b31afc8a
- https://github.com/mattermost/mattermost-plugin-playbooks
- https://mattermost.com/security-updates
