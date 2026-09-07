# [M] Mattermost Server exposes account details to any Team Administrator

## Summary
Severity: Medium
Advisory: GHSA-g3f3-p9rc-775p
CVE: CVE-2016-11080
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-g3f3-p9rc-775p
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <3.0.0

## Details
An issue was discovered in Mattermost Server before 3.0.0. It offers superfluous APIs for a Team Administrator to view account details.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-11080
- https://github.com/mattermost/mattermost/commit/6c75662b824491a20a757a5eec59556a866374b5
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
