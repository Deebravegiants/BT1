# [H] Mattermost doesn't enforce request body size limits on plugin HTTP endpoints

## Summary
Severity: High
Advisory: GHSA-jmvr-r5hm-fxfr
CVE: CVE-2026-5308
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-jmvr-r5hm-fxfr
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=11.6.0 <11.6.1
- Go: `github.com/mattermost/mattermost-server` — affected >=11.5.0 <11.5.4
- Go: `github.com/mattermost/mattermost-server` — affected >=11.4.0 <11.4.5
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.15
- Go: `github.com/mattermost/mattermost-plugin-github` — affected >=0 <1.0.1-0.20260410143745-9b41b1fd43c4

## Details
Mattermost versions 11.6.x <= 11.6.0, 11.5.x <= 11.5.3, 11.4.x <= 11.4.4, 10.11.x <= 10.11.14 fail to enforce request body size limits on plugin HTTP endpoints which allows an attacker to cause a denial of service via crafted oversized HTTP requests.. Mattermost Advisory ID: MMSA-2026-00646

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5308
- https://github.com/mattermost/mattermost-plugin-github/commit/9b41b1fd43c408f4be53026ee337bbeaa74ad47c
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
