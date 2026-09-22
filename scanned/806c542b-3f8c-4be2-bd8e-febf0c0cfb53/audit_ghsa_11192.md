# [M] Mattermost fails to properly enforce read permissions in search API endpoints

## Summary
Severity: Medium
Advisory: GHSA-cwfj-642j-gfh4
CVE: CVE-2026-24692
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-cwfj-642j-gfh4
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260107142155-0481bd1fb045
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20260107142155-0481bd1fb045
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0-rc1 <10.11.11
- Go: `github.com/mattermost/mattermost-server` — affected >=11.2.0-rc1 <11.2.3
- Go: `github.com/mattermost/mattermost-server` — affected >=11.3.0-rc1 <11.3.1

## Details
Mattermost versions 11.3.x <= 11.3.0, 11.2.x <= 11.2.2, 10.11.x <= 10.11.10 fail to properly enforce read permissions in search API endpoints which allows guest users without read permissions to access posts and files in channels via search API requests. Mattermost Advisory ID: MMSA-2025-00554

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-24692
- https://github.com/mattermost/mattermost/commit/0481bd1fb04584db97eca45fd58ebd06c8200df4
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
