# [M] Mattermost vulnerable to cross-site scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-63f2-6959-2pxj
CVE: CVE-2023-1776
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-31
Source: https://github.com/advisories/GHSA-63f2-6959-2pxj
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=6.0.0 <7.1.6
- Go: `github.com/mattermost/mattermost-server` — affected >=7.7.0 <7.7.2
- Go: `github.com/mattermost/mattermost-server` — affected >=7.1.0 <7.1.6
- Go: `github.com/mattermost/mattermost-server` — affected >=7.8.0 <7.8.1
- Go: `github.com/mattermost/mattermost-server/v5` — affected >=5.0.0 <7.1.6
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=3.3.0 <7.1.6

## Details
Boards in Mattermost allows an attacker to upload a malicious SVG image file as an attachment to a card and share it using a direct link to the file. 

[Issue Identifier](https://mattermost.com/security-updates/): MMSA-2023-00139

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1776
- https://github.com/mattermost/mattermost-server
- https://mattermost.com/security-updates
