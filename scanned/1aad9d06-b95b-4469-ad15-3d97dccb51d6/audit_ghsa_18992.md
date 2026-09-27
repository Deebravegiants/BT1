# [M] Mattermost does not enforce MFA on WebSocket connections

## Summary
Severity: Medium
Advisory: GHSA-xpg8-8xpv-948p
CVE: CVE-2025-55070
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-11-14
Source: https://github.com/advisories/GHSA-xpg8-8xpv-948p
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <11.1.0
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250912063506-7d8b7b5e4a60

## Details
Mattermost versions < 11 fail to enforce multi-factor authentication on WebSocket connections which allows unauthenticated users to access sensitive information via WebSocket events.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-55070
- https://github.com/mattermost/mattermost/commit/7d8b7b5e4a6076b2f7c87606883c417f9a610df5
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
