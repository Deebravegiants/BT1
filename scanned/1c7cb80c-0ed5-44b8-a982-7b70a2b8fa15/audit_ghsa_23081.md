# [M] Mattermost Server has Improper Authorization for Integration Requests

## Summary
Severity: Medium
Advisory: GHSA-x33g-375j-jhf7
CVE: CVE-2017-18916
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x33g-375j-jhf7
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <3.6.7-0.20170420152529-0968e4079e0a
- Go: `github.com/mattermost/mattermost-server` — affected >=3.7.0 <3.7.5
- Go: `github.com/mattermost/mattermost-server` — affected >=3.8.0 <3.8.2

## Details
An issue was discovered in Mattermost Server before 3.8.2, 3.7.5, and 3.6.7. API endpoint access control does not honor an integration permission restriction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18916
- https://github.com/mattermost/mattermost/commit/0968e4079e0aa670254f3fe3a7248d126e3cf877
- https://github.com/mattermost/mattermost/commit/b74e85653660525d351d090a1e1874ae933bcbc8
- https://github.com/mattermost/mattermost/commit/fb325cc339eb8d8efb60dbadc48fd38897201c6f
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
