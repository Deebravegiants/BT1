# [M] Improper Privilege Management in Mattermost

## Summary
Severity: Medium
Advisory: GHSA-qggc-pj29-j27m
CVE: CVE-2022-1332
CWE: CWE-200, CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-04-14
Source: https://github.com/advisories/GHSA-qggc-pj29-j27m
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=6.4.0 <6.4.2
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=6.3.0 <6.3.5
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=6.0.0 <6.2.5
- Go: `github.com/mattermost/mattermost-server/v5` — affected >=0 <5.37.9

## Details
One of the API in Mattermost version 6.4.1 and earlier fails to properly protect the permissions, which allows the authenticated members with restricted custom admin role to bypass the restrictions and view the server logs and server config.json file contents. Per the Mattermost security updates page, versions 6.4.2, 6.3.5, 6.2.5, and 5.37.9 contain patches for this issue

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1332
- https://github.com/mattermost/mattermost-server
- https://mattermost.com/security-updates
