# [H] Mattermost Server allows an attacker to specify a full pathname of a log file

## Summary
Severity: High
Advisory: GHSA-m2ch-x2q7-2284
CVE: CVE-2017-18912
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m2ch-x2q7-2284
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <3.7.4-0.20170404171331-0b5c0794fdcb

## Details
An issue was discovered in Mattermost Server before 3.7.5. It allows an attacker to specify a full pathname of a log file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18912
- https://github.com/mattermost/mattermost/commit/0b5c0794fdcbb551c1233dcdfbdf5c7deb585fd6
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
