# [M] Mattermost fails to limit the size of responses from integration action endpoints

## Summary
Severity: Medium
Advisory: GHSA-34g8-9fpp-46ch
CVE: CVE-2026-2456
CWE: CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-34g8-9fpp-46ch
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260127165411-fe3052073dc6
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20260127165411-fe3052073dc6
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0-rc1 <10.11.11
- Go: `github.com/mattermost/mattermost-server` — affected >=11.2.0-rc1 <11.2.3
- Go: `github.com/mattermost/mattermost-server` — affected >=11.3.0-rc1 <11.3.1

## Details
Mattermost versions 11.3.x <= 11.3.0, 11.2.x <= 11.2.2, 10.11.x <= 10.11.10 Mattermost fails to limit the size of responses from integration action endpoints, which allows an authenticated attacker to cause server memory exhaustion and denial of service via a malicious integration server that returns an arbitrarily large response when a user clicks an interactive message button. Mattermost Advisory ID: MMSA-2026-00571

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2456
- https://github.com/mattermost/mattermost/commit/fe3052073dc67e3c920baf9fe7efd44ac1d8124c
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
