# [M] Mattermost Incorrect Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-h69v-mvh9-hfrq
CVE: CVE-2023-5194
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-09-29
Source: https://github.com/advisories/GHSA-h69v-mvh9-hfrq
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.1.0 <8.1.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.0.0 <8.0.2
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0 <7.8.10

## Details
Mattermost fails to properly validate permissions when demoting and deactivating a user allowing for a system/user manager to demote / deactivate another manager

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5194
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
