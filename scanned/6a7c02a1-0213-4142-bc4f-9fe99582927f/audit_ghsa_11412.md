# [M] Mattermost doesn't rate limit login requests, allowing DoS

## Summary
Severity: Medium
Advisory: GHSA-247x-7qw8-fp98
CVE: CVE-2026-26233
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-247x-7qw8-fp98
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=11.4.0-rc1 <11.4.1
- Go: `github.com/mattermost/mattermost-server` — affected >=11.3.0-rc1 <11.3.2
- Go: `github.com/mattermost/mattermost-server` — affected >=11.2.0-rc1 <11.2.4
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0-rc1 <10.11.12

## Details
Mattermost versions 11.4.x <= 11.4.0, 11.3.x <= 11.3.1, 11.2.x <= 11.2.3, 10.11.x <= 10.11.11 fail to rate limit login requests which allows unauthenticated remote attackers to cause denial of service (server crash and restart) via HTTP/2 single packet attack with 100+ parallel login requests.. Mattermost Advisory ID: MMSA-2025-00566

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-26233
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
