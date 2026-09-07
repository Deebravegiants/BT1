# [M] Mattermost Server is vulnerable to XSS through author_link field in Slack attachments

## Summary
Severity: Medium
Advisory: GHSA-498j-wxww-j897
CVE: CVE-2017-18879
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-498j-wxww-j897
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.1.2
- Go: `github.com/mattermost/mattermost-server` — affected >=4.2.0 <4.2.1
- Go: `github.com/mattermost/mattermost-server` — affected >=4.3.0-rc1 <4.3.0

## Details
An issue was discovered in Mattermost Server before 4.3.0, 4.2.1, and 4.1.2. XSS could occur via the author_link field of a Slack attachment.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18879
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
