# [M] Mattermost fails to properly validate User-Agent header tokens

## Summary
Severity: Medium
Advisory: GHSA-2v3w-6g35-5f9v
CVE: CVE-2026-25783
CWE: CWE-1287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-2v3w-6g35-5f9v
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260129181235-1346cf529aef
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20260129181235-1346cf529aef
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0-rc1 <10.11.11
- Go: `github.com/mattermost/mattermost-server` — affected >=11.2.0-rc1 <11.2.3
- Go: `github.com/mattermost/mattermost-server` — affected >=11.3.0-rc1 <11.3.1

## Details
Mattermost versions 11.3.x <= 11.3.0, 11.2.x <= 11.2.2, 10.11.x <= 10.11.10 fail to properly validate User-Agent header tokens which allows an authenticated attacker to cause a request panic via a specially crafted User-Agent header. Mattermost Advisory ID: MMSA-2026-00586

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-25783
- https://github.com/mattermost/mattermost/commit/1346cf529aef0672c39a56ec10d1b8a9c8fb387d
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
