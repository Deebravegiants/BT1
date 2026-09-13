# [M] Mattermost users could access some sensitive information via API call

## Summary
Severity: Medium
Advisory: GHSA-7ggc-5r84-xf54
CVE: CVE-2022-2401
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-07-15
Source: https://github.com/advisories/GHSA-7ggc-5r84-xf54
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0 <6.3.9
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=6.4.0 <6.5.2
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=6.6.0 <6.6.2
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=6.7.0 <6.7.1

## Details
Unrestricted information disclosure of all users in Mattermost version 6.7.0 and earlier allows team members to access some sensitive information by directly accessing the APIs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2401
- https://github.com/mattermost/mattermost-server
- https://mattermost.com/security-updates
