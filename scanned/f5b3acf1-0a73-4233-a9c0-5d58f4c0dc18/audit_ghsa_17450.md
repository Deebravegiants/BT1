# [M] Mattermost fails to check Websocket request for proper UTF-8 format potentially crashing Calls plug-in

## Summary
Severity: Medium
Advisory: GHSA-j5vq-62gr-8v3r
CVE: CVE-2025-12689
CWE: CWE-1287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-12-17
Source: https://github.com/advisories/GHSA-j5vq-62gr-8v3r
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-plugin-calls` — affected >=0 <1.11.0

## Details
Mattermost versions 11.0.x <= 11.0.4, 10.12.x <= 10.12.2, 10.11.x <= 10.11.6 fail to check WebSocket request field for proper UTF-8 format, which allows attacker to crash Calls plug-in via sending malformed request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12689
- https://github.com/mattermost/mattermost-plugin-calls/commit/f68b41980e1274e05cf91c687e2af1a73c5e36ca
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
