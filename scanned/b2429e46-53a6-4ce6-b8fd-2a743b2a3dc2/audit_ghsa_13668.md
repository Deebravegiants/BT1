# [M] Mattermost password hash disclosure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r67m-mf7v-qp7j
CVE: CVE-2023-5968
CWE: CWE-116, CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-11-06
Source: https://github.com/advisories/GHSA-r67m-mf7v-qp7j
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=5.4.0-rc1 <7.8.12
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.0.0 <8.0.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.1.0 <8.1.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.0.0 <9.0.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20230825233148-f787fd63368a
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0 <5.3.2-0.20230825233148-f787fd63368a
- Go: `github.com/mattermost/mattermost-server/v5` — affected >=0 <5.3.2-0.20230825233148-f787fd63368a
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20230825233148-f787fd63368a

## Details
Mattermost fails to properly sanitize the user object when updating the username, resulting in the password hash being included in the response body.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5968
- https://github.com/mattermost/mattermost/pull/24362
- https://github.com/mattermost/mattermost/pull/24566
- https://github.com/mattermost/mattermost/commit/698f4a97da564e2c1f2bf1fbd01755cefa3b7881
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
