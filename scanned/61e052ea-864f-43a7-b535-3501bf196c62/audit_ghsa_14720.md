# [M] Mattermost Improper Validation of Specified Type of Input vulnerability

## Summary
Severity: Medium
Advisory: GHSA-69pr-78gv-7c6h
CVE: CVE-2024-54083
CWE: CWE-1287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-12-16
Source: https://github.com/advisories/GHSA-69pr-78gv-7c6h
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.1.0 <10.1.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.0.0 <10.0.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.11.0 <9.11.5
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.5.0 <9.5.13

## Details
Mattermost versions 10.1.x <= 10.1.2, 10.0.x <= 10.0.2, 9.11.x <= 9.11.4, 9.5.x <= 9.5.12 fail to properly validate the type of callProps which allows a user to cause a client side (webapp and mobile) DoS to users of particular channels, by sending a specially crafted post.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-54083
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
