# [M] Mattermost doesn't properly validate CSRF tokens

## Summary
Severity: Medium
Advisory: GHSA-rmhw-c3xr-m3xx
CVE: CVE-2026-27659
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-rmhw-c3xr-m3xx
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.4.0-rc1 <11.4.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.3.0-rc1 <11.3.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.2.0-rc1 <11.2.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.11.0-rc1 <10.11.11
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.0.0-20260105080200-d27a2195068d <10.11.11

## Details
Mattermost versions 11.2.x <= 11.2.2, 10.11.x <= 10.11.10, 11.4.x <= 11.4.0, 11.3.x <= 11.3.1 fail to properly validate CSRF tokens in the /api/v4/access_control_policies/{policy_id}/activate endpoint, which allows an attacker to trick an admin into changing access control policy active status via a crafted request. Mattermost Advisory ID: MMSA-2026-00578

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-27659
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
