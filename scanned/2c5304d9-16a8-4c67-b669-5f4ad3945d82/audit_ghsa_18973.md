# [M] Mattermost fails to sanitize team email addresses

## Summary
Severity: Medium
Advisory: GHSA-4g87-9x45-cx2h
CVE: CVE-2025-12559
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-11-27
Source: https://github.com/advisories/GHSA-4g87-9x45-cx2h
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20251015091448-abbf01b9db45
- Go: `github.com/mattermost/mattermost-server` — affected >=11.0.0 <11.0.3
- Go: `github.com/mattermost/mattermost-server` — affected >=10.12.0 <10.12.2
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.5
- Go: `github.com/mattermost/mattermost-server` — affected >=10.5.0 <10.5.13

## Details
Mattermost versions 11.0.x <= 11.0.2, 10.12.x <= 10.12.1, 10.11.x <= 10.11.4, 10.5.x <= 10.5.12 fail to sanitize team email addresses to be visible only to Team Admins, which allows any authenticated user to view team email addresses via the GET /api/v4/channels/{channel_id}/common_teams endpoint

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12559
- https://github.com/mattermost/mattermost/pull/34110
- https://github.com/mattermost/mattermost/commit/5d8719042c1807da59ac8a821624eb01152d8495
- https://github.com/mattermost/mattermost/commit/649aee8fa9184ca59bd66022a33b8f8918e413aa
- https://github.com/mattermost/mattermost/commit/7ccb62db7958abd6a4b21a06c5a4f5367a8f8b1f
- https://github.com/mattermost/mattermost/commit/9f54e5cdc3aef412945ff0e6a58338f7b549bdda
- https://github.com/mattermost/mattermost/commit/abbf01b9db45d1850eaf3701ea8362b910193ffd
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
