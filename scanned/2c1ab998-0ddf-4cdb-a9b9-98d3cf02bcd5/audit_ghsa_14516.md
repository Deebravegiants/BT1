# [M] Mattermost vulnerable to information disclosure

## Summary
Severity: Medium
Advisory: GHSA-3wq5-3f56-v5xc
CVE: CVE-2023-1777
CWE: CWE-668
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-03-31
Source: https://github.com/advisories/GHSA-3wq5-3f56-v5xc
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=6.3.0 <7.1.6
- Go: `github.com/mattermost/mattermost-server` — affected >=7.8.0 <7.8.1
- Go: `github.com/mattermost/mattermost-server` — affected >=7.7.0 <7.7.2
- Go: `github.com/mattermost/mattermost-server` — affected >=7.1.0 <7.1.6
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=6.0.0-20211025164829-f7a8147b825c <6.0.0-20230301145909-10be118d99a5
- Go: `github.com/mattermost/mattermost-server` — affected >=1.4.1-0.20211025164829-f7a8147b825c <1.4.1-0.20230301145909-10be118d99a5

## Details
Mattermost allows an attacker to request a preview of an existing message when creating a new message via the createPost API call, disclosing the contents of the linked message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1777
- https://mattermost.com/security-updates
- github.com/mattermost/mattermost-server
