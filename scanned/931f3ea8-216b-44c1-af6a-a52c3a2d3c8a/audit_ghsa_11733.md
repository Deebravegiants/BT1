# [M] Mattermost allows system administrators to read arbitrary host files via malicious AdvancedLoggingJSON configuration

## Summary
Severity: Medium
Advisory: GHSA-3mw5-466q-295q
CVE: CVE-2026-3112
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-3mw5-466q-295q
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.4.0-rc1 <11.4.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.3.0-rc1 <11.3.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.2.0-rc1 <11.2.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.11.0-rc1 <10.11.12
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.0.0-20260105080200-d27a2195068d <8.0.0-20260217110922-b7d4a1f1f59b

## Details
Mattermost versions 11.4.x <= 11.4.0, 11.3.x <= 11.3.1, 11.2.x <= 11.2.3, 10.11.x <= 10.11.11 fail to validate Advanced Logging file target paths which allows system administrators to read arbitrary host files via malicious AdvancedLoggingJSON configuration in support packet generation. Mattermost Advisory ID: MMSA-2025-00562.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3112
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
