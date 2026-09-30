# [M] Mattermost Missing Authentication for Critical Function

## Summary
Severity: Medium
Advisory: GHSA-7h34-9chr-58qh
CVE: CVE-2025-6226
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-07-18
Source: https://github.com/advisories/GHSA-7h34-9chr-58qh
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=10.5.0 <10.5.7
- Go: `github.com/mattermost/mattermost-server` — affected >=10.8.0 <10.8.2
- Go: `github.com/mattermost/mattermost-server` — affected >=10.7.0 <10.7.4
- Go: `github.com/mattermost/mattermost-server` — affected >=9.11.0 <9.11.17
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250520130510-fa40a8c5d47f

## Details
Mattermost versions 10.5.x <= 10.5.6, 10.8.x <= 10.8.1, 10.7.x <= 10.7.3, 9.11.x <= 9.11.16 fail to verify authorization when retrieving cached posts by PendingPostID which allows an authenticated user to read posts in private channels they don't have access to via guessing the PendingPostID of recently created posts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6226
- https://github.com/mattermost/mattermost/commit/fa40a8c5d47fed5c166429a1c1bd95d62b241d89
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
