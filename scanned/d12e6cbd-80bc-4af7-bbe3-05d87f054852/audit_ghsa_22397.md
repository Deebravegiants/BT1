# [H] Mattermost Server uses weak hashing for OAuth, email verification tokens and invitations

## Summary
Severity: High
Advisory: GHSA-jxc4-w54c-qv5r
CVE: CVE-2017-18917
CWE: CWE-328
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jxc4-w54c-qv5r
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <3.7.5-0.20170421192444-247cd1e51a8c
- Go: `github.com/mattermost/mattermost-server` — affected >=3.8.0 <3.8.2

## Details
An issue was discovered in Mattermost Server before 3.8.2 and 3.7.5. Weak hashing was used for e-mail invitations, OAuth, and e-mail verification tokens.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18917
- https://github.com/mattermost/mattermost/commit/247cd1e51a8c943628dc650e87e794b06aad4c2b
- https://github.com/mattermost/mattermost/commit/b74e85653660525d351d090a1e1874ae933bcbc8
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
