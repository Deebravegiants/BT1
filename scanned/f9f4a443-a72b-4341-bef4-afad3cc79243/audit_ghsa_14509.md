# [M] Mattermost fails to properly authentication inviter's permissions to private channel

## Summary
Severity: Medium
Advisory: GHSA-9hj7-v56g-rhf6
CVE: CVE-2023-1774
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-31
Source: https://github.com/advisories/GHSA-9hj7-v56g-rhf6
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=3.3.0 <7.1.6
- Go: `github.com/mattermost/mattermost-server` — affected >=7.7.0 <7.7.2
- Go: `github.com/mattermost/mattermost-server` — affected >=7.1.0 <7.1.6
- Go: `github.com/mattermost/mattermost-server/v5` — affected >=5.0.0 <7.1.6
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=6.0.0 <7.1.6

## Details
When processing an email invite to a private channel on a team, Mattermost fails to validate the inviter's permission to that channel, allowing an attacker to invite themselves to a private channel.

[Issue Identifier](https://mattermost.com/security-updates/): MMSA-2023-00137

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1774
- https://mattermost.com/security-updates
- github.com/mattermost/mattermost-server
