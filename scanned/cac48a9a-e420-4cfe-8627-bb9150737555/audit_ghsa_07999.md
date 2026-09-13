# [M] Mattermost fails to properly validate login method restrictions

## Summary
Severity: Medium
Advisory: GHSA-3c9r-7f29-qp32
CVE: CVE-2026-0999
CWE: CWE-303
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-16
Source: https://github.com/advisories/GHSA-3c9r-7f29-qp32
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20251212052346-61651b0df7ea
- Go: `github.com/mattermost/mattermost-server` — affected >=11.1.0
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0
- Go: `github.com/mattermost/mattermost-server` — affected >=11.2.0
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20251212052346-61651b0df7ea

## Details
Mattermost versions 11.1.x <= 11.1.2, 10.11.x <= 10.11.9, 11.2.x <= 11.2.1 fail to properly validate login method restrictions which allows an authenticated user to bypass SSO-only login requirements via userID-based authentication. Mattermost Advisory ID: MMSA-2025-00548

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-0999
- https://github.com/mattermost/mattermost/commit/61651b0df7ea5db55d1e54f8d6fb5fce4149309c
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
