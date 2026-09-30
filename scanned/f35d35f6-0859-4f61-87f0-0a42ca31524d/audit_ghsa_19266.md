# [M] Mattermost fails to properly invalidate personal access tokens upon user deactivation

## Summary
Severity: Medium
Advisory: GHSA-mc2f-jgj6-6cp3
CVE: CVE-2025-3230
CWE: CWE-303
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-05-30
Source: https://github.com/advisories/GHSA-mc2f-jgj6-6cp3
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.7.0-rc1 <10.7.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.6.0-rc1 <10.6.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.0.0-rc1 <10.5.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.0.0-rc1 <9.11.13
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250402193107-65343f84a783

## Details
Mattermost versions 10.7.x <= 10.7.0, 10.6.x <= 10.6.2, 10.5.x <= 10.5.3, 9.11.x <= 9.11.12 fails to properly invalidate personal access tokens upon user deactivation, allowing deactivated users to maintain full system access by exploiting access token validation flaws via continued usage of previously issued tokens.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3230
- https://github.com/mattermost/mattermost/commit/65343f84a7830fa8078fe3df879fca924e4fac01
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
