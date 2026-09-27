# [C] Mattermost Server server restarts may provide attackers with API access

## Summary
Severity: Critical
Advisory: GHSA-hxxj-8phw-74vw
CVE: CVE-2017-18915
CWE: CWE-20, CWE-807
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hxxj-8phw-74vw
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <3.6.7-0.20170420152529-0968e4079e0a
- Go: `github.com/mattermost/mattermost-server` — affected >=3.7.0 <3.7.5
- Go: `github.com/mattermost/mattermost-server` — affected >=3.8.0 <3.8.2

## Details
An issue was discovered in Mattermost Server before 3.8.2, 3.7.5, and 3.6.7. After a restart of a server, an attacker might suddenly gain API Endpoint access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18915
- https://github.com/mattermost/mattermost/commit/0968e4079e0aa670254f3fe3a7248d126e3cf877
- https://github.com/mattermost/mattermost/commit/c7bdce8a6641ed8d361a43b6004a351535c78423
- https://github.com/mattermost/mattermost/commit/fb325cc339eb8d8efb60dbadc48fd38897201c6f
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
