# [M] Mattermost Server does not restrict SAML certificate path for System Administrators

## Summary
Severity: Medium
Advisory: GHSA-5ghq-28r7-qwfj
CVE: CVE-2017-18918
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5ghq-28r7-qwfj
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <3.6.5
- Go: `github.com/mattermost/mattermost-server` — affected >=3.7.0 <3.7.3

## Details
An issue was discovered in Mattermost Server before 3.7.3 and 3.6.5. A System Administrator can place a SAML certificate at an arbitrary pathname.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18918
- https://github.com/mattermost/mattermost/commit/8ec37570742b67fd640bb3434ea226c655dbf408
- https://github.com/mattermost/mattermost/commit/a12e7fdca439948ab097431d68e8f59778fbab81
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
