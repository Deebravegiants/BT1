# [M] Mattermost allows remote/synthetic users to create sessions, reset passwords

## Summary
Severity: Medium
Advisory: GHSA-c6vp-jjgv-38wj
CVE: CVE-2024-39836
CWE: CWE-693
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-22
Source: https://github.com/advisories/GHSA-c6vp-jjgv-38wj
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.9.0 <9.9.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.5.0 <9.5.8
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.10.0 <9.10.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.8.0 <9.8.3

## Details
Mattermost versions 9.9.x <= 9.9.1, 9.5.x <= 9.5.7, 9.10.x <= 9.10.0 and 9.8.x <= 9.8.2 fail to  ensure that remote/synthetic users cannot create sessions or reset passwords, which allows the munged email addresses, created by shared channels, to be used to receive email notifications and to reset passwords, when they are valid, functional emails.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39836
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
