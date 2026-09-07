# [M] Mattermost Server has Insufficient Session Expiration when used as an OAuth 2.0 service provider

## Summary
Severity: Medium
Advisory: GHSA-g24c-fx4v-xg9w
CVE: CVE-2017-18905
CWE: CWE-613
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-g24c-fx4v-xg9w
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <3.9.2
- Go: `github.com/mattermost/mattermost-server` — affected >=3.10.0 <3.10.2

## Details
An issue was discovered in Mattermost Server before 4.0.0, 3.10.2, and 3.9.2, when used as an OAuth 2.0 service provider, Session invalidation was mishandled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18905
- https://github.com/mattermost/mattermost/commit/15ad24d160cb4604d0605ebbfa53d11a57820706
- https://github.com/mattermost/mattermost/commit/b17fca0d5ee7557e3df1cf1d1da8bd749859e35f
- https://github.com/mattermost/mattermost/commit/fbc170733e86f09b46ba754dd03304733d2f482f
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
