# [H] Mattermost Server is vulnerable to a Denial of Service attack through `invite_people` command

## Summary
Severity: High
Advisory: GHSA-5mh6-p63g-3mv5
CVE: CVE-2018-21258
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5mh6-p63g-3mv5
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.1.0

## Details
An issue was discovered in Mattermost Server before 5.1.0. It allows attackers to cause a denial of service via the invite_people slash command.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-21258
- https://github.com/mattermost/mattermost/commit/af615ffc24b774d76deef8c93282831432669dd8
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
