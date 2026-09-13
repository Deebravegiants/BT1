# [M] Mattermost doesn't limit the size of the request body on the start meeting API endpoint

## Summary
Severity: Medium
Advisory: GHSA-m3p3-8frq-q7qh
CVE: CVE-2026-2325
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-m3p3-8frq-q7qh
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=11.5.0 <11.5.2
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.14
- Go: `github.com/mattermost/mattermost-server` — affected >=11.4.0 <11.4.4
- Go: `github.com/mattermost/mattermost-plugin-msteams-meetings` — affected >=0 <1.1.1-0.20260213105619-c5892dd169de

## Details
Mattermost versions 11.5.x <= 11.5.1, 10.11.x <= 10.11.13, 11.4.x <= 11.4.3 fail to limit the size of the request body on the start meeting API endpoint, which allows an authenticated attacker to cause resource exhaustion or denial of service via a crafted oversized HTTP POST request to {{/api/v1/meetings}}.. Mattermost Advisory ID: MMSA-2026-00608

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2325
- https://github.com/mattermost/mattermost-plugin-msteams-meetings/commit/c5892dd169de865504afa2dd02eaeb6287489f7f
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
