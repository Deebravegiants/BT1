# [M] Mattermost allows authenticated guest users to enumerate user IDs outside their allowed visibility scope

## Summary
Severity: Medium
Advisory: GHSA-mpc7-mm28-f6wq
CVE: CVE-2026-3115
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-mpc7-mm28-f6wq
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.4.0 <11.4.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.3.0-rc1 <11.3.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.2.0-rc1 <11.2.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.11.0-rc1 <10.11.11
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.0.0-20260105080200-d27a2195068d <8.0.0-20260217110922-b7d4a1f1f59b

## Details
Mattermost versions 11.2.x <= 11.2.2, 10.11.x <= 10.11.10, 11.4.x <= 11.4.0, 11.3.x <= 11.3.1 fail to apply view restrictions when retrieving group member IDs, which allows authenticated guest users to enumerate user IDs outside their allowed visibility scope via the group retrieval endpoint. Mattermost Advisory ID: MMSA-2026-00594.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3115
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
