# [M] Mattermost allows attackers to spoof permalink embeds

## Summary
Severity: Medium
Advisory: GHSA-ph22-fw5m-w2q9
CVE: CVE-2026-2457
CWE: CWE-346
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-ph22-fw5m-w2q9
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260123211116-9efe617be8b8
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20260123211116-9efe617be8b8
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0-rc1 <10.11.11
- Go: `github.com/mattermost/mattermost-server` — affected >=11.2.0-rc1 <11.2.3
- Go: `github.com/mattermost/mattermost-server` — affected >=11.3.0-rc1 <11.3.1

## Details
Mattermost versions 11.3.x <= 11.3.0, 11.2.x <= 11.2.2, 10.11.x <= 10.11.10 fail to sanitize client-supplied post metadata which allows an authenticated attacker to spoof permalink embeds impersonating other users via crafted PUT requests to the post update API endpoint. Mattermost Advisory ID: MMSA-2025-00569

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2457
- https://github.com/mattermost/mattermost/commit/9efe617be8b8f1d036e12721e8e73b69a543ed34
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
