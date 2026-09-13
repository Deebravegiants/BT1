# [M] Mattermost has session spoofing due to lack of single-use consumption of guest magic link tokens enforcement

## Summary
Severity: Medium
Advisory: GHSA-mh4x-rmrx-3hp4
CVE: CVE-2026-3590
CWE: CWE-367
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-mh4x-rmrx-3hp4
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.0.0-20250721062209-4952acea88ce <8.0.0-20250723052842-4cb8d8940332
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0-rc1 <10.11.13
- Go: `github.com/mattermost/mattermost-server` — affected >=11.5.0-rc1 <11.5.0
- Go: `github.com/mattermost/mattermost-server` — affected >=11.4.0-rc1 <11.4.3
- Go: `github.com/mattermost/mattermost-server` — affected >=11.3.0-rc1 <11.3.3

## Details
Mattermost versions 10.11.x <= 10.11.12, 11.5.x <= 11.5.0, 11.4.x <= 11.4.2, 11.3.x <= 11.3.2 fail to enforce atomic single-use consumption of guest magic link tokens, which allows an attacker with access to a valid magic link to establish multiple independent authenticated sessions via concurrent requests. Mattermost Advisory ID: MMSA-2026-00624.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3590
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
