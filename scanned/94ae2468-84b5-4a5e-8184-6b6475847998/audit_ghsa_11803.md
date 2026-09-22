# [M] Mattermost allows a removed team member to enumerate all public channels within a private team

## Summary
Severity: Medium
Advisory: GHSA-679f-wmrg-qf57
CVE: CVE-2026-2458
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-679f-wmrg-qf57
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260113182106-a18b80ba4c32
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20260113182106-a18b80ba4c32
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0-rc1 <10.11.11
- Go: `github.com/mattermost/mattermost-server` — affected >=11.2.0-rc1 <11.2.3
- Go: `github.com/mattermost/mattermost-server` — affected >=11.3.0-rc1 <11.3.1

## Details
Mattermost versions 11.3.x <= 11.3.0, 11.2.x <= 11.2.2, 10.11.x <= 10.11.10 fail to properly validate team membership when searching channels which allows a removed team member to enumerate all public channels within a private team via the channel search API endpoint. Mattermost Advisory ID: MMSA-2025-00568

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2458
- https://github.com/mattermost/mattermost/commit/a18b80ba4c324b74b3d47951c33957305af4a099
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
