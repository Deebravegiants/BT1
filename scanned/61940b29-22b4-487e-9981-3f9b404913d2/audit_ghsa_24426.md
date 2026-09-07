# [M] Mattermost Server does not prevent System Admin from arbitrary file creation

## Summary
Severity: Medium
Advisory: GHSA-9rr5-q43r-ccv4
CVE: CVE-2017-18875
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9rr5-q43r-ccv4
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.1.2-0.20171004201910-6be8113eb60c
- Go: `github.com/mattermost/mattermost-server` — affected >=4.2.0-rc1.0.20171004154238-fadd9514f6e7 <4.2.1-0.20171004194140-6d3cb2ce07fc
- Go: `github.com/mattermost/mattermost-server` — affected >=4.3.0-rc1 <4.3.0

## Details
An issue was discovered in Mattermost Server before 4.3.0, 4.2.1, and 4.1.2 when local storage for files is used. A System Admin can create arbitrary files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18875
- https://github.com/mattermost/mattermost/commit/6be8113eb60cf5ddd2dc1c3f4db05cae0c183086
- https://github.com/mattermost/mattermost/commit/6d3cb2ce07fc799832081e93843b405b390057fa
- https://github.com/mattermost/mattermost/commit/fadd9514f6e71590aba781a7035e1de4150137b0
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
