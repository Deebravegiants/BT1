# [M] Mattermost fails to limit the number of active sessions

## Summary
Severity: Medium
Advisory: GHSA-wj37-mpq9-xrcm
CVE: CVE-2024-4183
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-04-26
Source: https://github.com/advisories/GHSA-wj37-mpq9-xrcm
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=9.6.0-rc1 <9.6.1
- Go: `github.com/mattermost/mattermost-server` — affected >=9.5.0 <9.5.3
- Go: `github.com/mattermost/mattermost-server` — affected >=9.4.0 <9.4.5
- Go: `github.com/mattermost/mattermost-server` — affected >=8.1.0 <8.1.12

## Details
Mattermost versions 8.1.x before 8.1.12, 9.6.x before 9.6.1, 9.5.x before 9.5.3, 9.4.x before 9.4.5 fail to limit the number of active sessions, which allows an authenticated attacker to crash the server via repeated requests to the getSessions API after flooding the sessions table.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-4183
- https://github.com/mattermost/mattermost/commit/86920d641760552c5aafa5e1d14c93bd30039bc4
- https://github.com/mattermost/mattermost/commit/9d81eee979aee93374bff8ba6714d805e12ffb03
- https://github.com/mattermost/mattermost/commit/b45c3dac4c160992a1ce757ade968e8f5ec506c1
- https://github.com/mattermost/mattermost/commit/bc699e6789cf3ba1544235087897699aaa639e7d
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
