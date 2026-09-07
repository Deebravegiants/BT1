# [H] Mattermost Server vulnerable to user account takeover when Single Sign-On OAuth2 is used

## Summary
Severity: High
Advisory: GHSA-fpcr-4rr5-hpcp
CVE: CVE-2017-18906
CWE: CWE-613
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fpcr-4rr5-hpcp
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <3.9.2-0.20170714134023-b17fca0d5ee7
- Go: `github.com/mattermost/mattermost-server` — affected >=3.10.0 <3.10.2

## Details
An issue was discovered in Mattermost Server before 4.0.0, 3.10.2, and 3.9.2, when Single Sign-On OAuth2 is used. An attacker could claim somebody else's account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18906
- https://github.com/mattermost/mattermost/commit/259ad46f30d0fac2f7c5c14f3b76b2170f7e90c7
- https://github.com/mattermost/mattermost/commit/b17fca0d5ee7557e3df1cf1d1da8bd749859e35f
- https://github.com/mattermost/mattermost/commit/fbc170733e86f09b46ba754dd03304733d2f482f
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
