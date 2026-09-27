# [M] Mattermost Server Sensitive Data Exposure

## Summary
Severity: Medium
Advisory: GHSA-j2h2-cvwh-cr64
CVE: CVE-2020-14457
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-j2h2-cvwh-cr64
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server/v5` — affected >=0 <5.20.0

## Details
An issue was discovered in Mattermost Server before 5.20.0. Non-members can receive broadcasted team details via the `update_team` WebSocket event, aka MMSA-2020-0012.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14457
- https://github.com/mattermost/mattermost/pull/13848
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
