# [M] Mattermost fails to check if user is a guest before performing actions on public playbooks

## Summary
Severity: Medium
Advisory: GHSA-p267-jjfq-pphf
CVE: CVE-2023-4106
CWE: CWE-284, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-08-11
Source: https://github.com/advisories/GHSA-p267-jjfq-pphf
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=7.9.0 <7.9.6
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=7.10.0 <7.10.4
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0 <7.8.8

## Details
Mattermost fails to check if the requesting user is a guest before performing different actions to public playbooks, resulting a guest being able to view, join, edit, export and archive public playbooks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-4106
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
