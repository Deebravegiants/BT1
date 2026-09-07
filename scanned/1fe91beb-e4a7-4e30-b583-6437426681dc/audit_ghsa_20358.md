# [M] Uncontrolled Resource Consumption in Mattermost server

## Summary
Severity: Medium
Advisory: GHSA-gwpf-95jc-63rv
CVE: CVE-2022-1982
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-03
Source: https://github.com/advisories/GHSA-gwpf-95jc-63rv
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=6.6.0 <6.6.1
- Go: `github.com/mattermost/mattermost-server` — affected >=6.5.0 <6.5.1
- Go: `github.com/mattermost/mattermost-server` — affected >=6.4.0 <6.4.3
- Go: `github.com/mattermost/mattermost-server` — affected >=5.0.0 <6.3.8

## Details
Uncontrolled resource consumption in Mattermost version 6.6.0 and earlier allows an authenticated attacker to crash the server via a crafted SVG attachment on a post.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1982
- https://github.com/mattermost/mattermost-server/pull/19988
- https://github.com/mattermost/mattermost-server
- https://mattermost.com/security-updates
