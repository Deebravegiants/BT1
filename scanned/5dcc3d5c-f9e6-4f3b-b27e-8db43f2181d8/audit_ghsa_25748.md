# [C] Command Injection in CasaOS

## Summary
Severity: Critical
Advisory: GHSA-jh63-28gx-7p26
CVE: CVE-2022-24193
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-11
Source: https://github.com/advisories/GHSA-jh63-28gx-7p26
Type: github-advisory

## Affected
- Go: `github.com/IceWhaleTech/CasaOS` — affected >=0 <0.2.8

## Details
CasaOS before v0.2.7 was discovered to contain a command injection vulnerability via the component leave or join zerotier api.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24193
- https://github.com/IceWhaleTech/CasaOS/issues/84
- https://github.com/IceWhaleTech/CasaOS/commit/d060968b7ab08e7f8cbfe7ca9ccdfa47afe9bb06
- https://github.com/IceWhaleTech/CasaOS
- https://www.star123.top/2022/01/08/A-vulnerability-in-CasaOS
- https://www.star123.top/2022/01/08/A-vulnerability-in-CasaOS/#more
