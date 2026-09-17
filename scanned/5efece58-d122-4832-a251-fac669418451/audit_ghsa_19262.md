# [M] Mattermost fails to clear Google OAuth credentials

## Summary
Severity: Medium
Advisory: GHSA-8cgx-9ccj-3gwr
CVE: CVE-2025-2571
CWE: CWE-303
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-05-30
Source: https://github.com/advisories/GHSA-8cgx-9ccj-3gwr
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.7.0-rc1 <10.7.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.0.0-rc1 <10.5.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.0.0-rc1 <9.11.13
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250414095146-04676582cdd2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.6.0-rc1 <10.6.3

## Details
Mattermost versions 10.7.x <= 10.7.0, 10.6.x <= 10.6.2, 10.5.x <= 10.5.3, 9.11.x <= 9.11.12 fail to clear Google OAuth credentials when converting user accounts to bot accounts, allowing attackers to gain unauthorized access to bot accounts via the Google OAuth signup flow.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2571
- https://github.com/mattermost/mattermost/commit/04676582cdd26f4fdfa78fcf60a7f8745e6b27f5
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
