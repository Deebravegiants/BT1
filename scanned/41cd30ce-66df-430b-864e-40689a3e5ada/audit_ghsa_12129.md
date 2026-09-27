# [H] Mattermost fails to properly handle very long passwords

## Summary
Severity: High
Advisory: GHSA-m5rv-56xx-hfc6
CVE: CVE-2026-24458
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-m5rv-56xx-hfc6
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260129164748-7201f42d955f
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20260129164748-7201f42d955f
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0-rc1 <10.11.11
- Go: `github.com/mattermost/mattermost-server` — affected >=11.2.0-rc1 <11.2.3
- Go: `github.com/mattermost/mattermost-server` — affected >=11.3.0-rc1 <11.3.1

## Details
Mattermost versions 11.3.x <= 11.3.0, 11.2.x <= 11.2.2, 10.11.x <= 10.11.10 fail to properly handle very long passwords, which allows an attacker to overload the server CPU and memory via executing login attempts with multi-megabyte passwords. Mattermost Advisory ID: MMSA-2026-00587

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-24458
- https://github.com/mattermost/mattermost/commit/7201f42d955f1bc44719b862132546626b60a180
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
