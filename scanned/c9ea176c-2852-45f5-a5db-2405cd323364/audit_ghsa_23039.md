# [M] Mattermost Server allows users with a session ID to revoke another users' session

## Summary
Severity: Medium
Advisory: GHSA-h564-6gc2-fcc6
CVE: CVE-2017-18878
CWE: CWE-284, CWE-639, CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h564-6gc2-fcc6
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.1.2-0.20171004201910-6be8113eb60c
- Go: `github.com/mattermost/mattermost-server` — affected >=4.2.0-rc1 <4.2.1-0.20171004192657-8fbbd688ea24
- Go: `github.com/mattermost/mattermost-server` — affected >=4.3.0-rc1 <4.3.0

## Details
An issue was discovered in Mattermost Server before 4.3.0, 4.2.1, and 4.1.2. Knowledge of a session ID allows revoking another user's session.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18878
- https://github.com/mattermost/mattermost/commit/6be8113eb60cf5ddd2dc1c3f4db05cae0c183086
- https://github.com/mattermost/mattermost/commit/8fbbd688ea2466dd0d70e9c07e9703d78f8a19a5
- https://github.com/mattermost/mattermost/commit/affd35071ea155069979fd359726296de8aa6aaf
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
