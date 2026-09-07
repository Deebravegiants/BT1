# [M] Mattermost Server exposes sensitive information about team URLs via an API

## Summary
Severity: Medium
Advisory: GHSA-q3g9-hgrx-hwhx
CVE: CVE-2016-11075
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q3g9-hgrx-hwhx
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <2.0.1-0.20160310160916-26ad6d2c7696

## Details
An issue was discovered in Mattermost Server before 3.0.0. It allows attackers to obtain sensitive information about team URLs via an API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-11075
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
