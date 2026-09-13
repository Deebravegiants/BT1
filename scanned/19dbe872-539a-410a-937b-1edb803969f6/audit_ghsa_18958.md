# [M] Mattermost fails to properly restrict access to archived channel search API

## Summary
Severity: Medium
Advisory: GHSA-j6gg-r5jc-47cm
CVE: CVE-2025-11776
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-11-14
Source: https://github.com/advisories/GHSA-j6gg-r5jc-47cm
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250815165020-c8d66301415d
- Go: `github.com/mattermost/mattermost` — affected >=0 <5.3.2-0.20250815165020-c8d66301415d
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20250815165020-c8d66301415d
- Go: `github.com/mattermost/mattermost-server/v5` — affected >=0 <5.3.2-0.20250815165020-c8d66301415d
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0 <5.3.2-0.20250815165020-c8d66301415d

## Details
Mattermost versions < 11 fail to properly restrict access to archived channel search API which allows guest users to discover archived public channels via the `/api/v4/teams/{team_id}/channels/search_archived` endpoint

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11776
- https://github.com/mattermost/mattermost/commit/c8d66301415d5b447df0e829bdbaa92e8a83ecf8
- https://mattermost.com/security-updates
- github.com/mattermost/mattermost
