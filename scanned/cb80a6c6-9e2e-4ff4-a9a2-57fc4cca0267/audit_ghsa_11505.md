# [M] Mattermost fails to filter invite IDs based on user permissions

## Summary
Severity: Medium
Advisory: GHSA-fx49-m253-27jj
CVE: CVE-2026-2463
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-fx49-m253-27jj
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260105134819-cc427af41b2a
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20260105134819-cc427af41b2a
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0-rc1 <10.11.11
- Go: `github.com/mattermost/mattermost-server` — affected >=11.2.0-rc1 <11.2.3
- Go: `github.com/mattermost/mattermost-server` — affected >=11.3.0-rc1 <11.3.1

## Details
Mattermost versions 11.3.x <= 11.3.0, 11.2.x <= 11.2.2, 10.11.x <= 10.11.10 fail to filter invite IDs based on user permissions, which allows regular users to bypass access control restrictions and register unauthorized accounts via leaked invite IDs during team creation. Mattermost Advisory ID: MMSA-2025-00565

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2463
- https://github.com/mattermost/mattermost/commit/cc427af41b2a8d3a552d8dc42978831dcfecc1d8
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
