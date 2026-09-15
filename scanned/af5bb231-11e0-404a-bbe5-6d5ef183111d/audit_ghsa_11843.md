# [M] Mattermost fails to canonicalize IPv4-mapped IPv6 addresses before reserved IP validation

## Summary
Severity: Medium
Advisory: GHSA-gqv7-j2j8-qmwq
CVE: CVE-2026-2455
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-gqv7-j2j8-qmwq
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260129133647-5d787969c2d5
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20260129133647-5d787969c2d5
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0-rc1 <10.11.11
- Go: `github.com/mattermost/mattermost-server` — affected >=11.2.0-rc1 <11.2.3
- Go: `github.com/mattermost/mattermost-server` — affected >=11.3.0-rc1 <11.3.1

## Details
Mattermost versions 11.3.x <= 11.3.0, 11.2.x <= 11.2.2, 10.11.x <= 10.11.10 fail to canonicalize IPv4-mapped IPv6 addresses before reserved IP validation which allows an attacker to perform SSRF attacks against internal services via IPv4-mapped IPv6 literals (e.g., [::ffff:127.0.0.1]).. Mattermost Advisory ID: MMSA-2026-00585

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2455
- https://github.com/mattermost/mattermost/commit/5d787969c2d5ab591a9dcd61b0810475eed7a646
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
