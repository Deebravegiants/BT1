# [M] Improper Restriction of XML External Entity Reference in trytond and proteus

## Summary
Severity: Medium
Advisory: GHSA-cj78-rgw3-4h5p
CVE: CVE-2022-26661
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-11
Source: https://github.com/advisories/GHSA-cj78-rgw3-4h5p
Type: github-advisory

## Affected
- PyPI: `trytond` — affected >=5.0.0 <5.0.46
- PyPI: `trytond` — affected >=6.0.0 <6.0.16
- PyPI: `trytond` — affected >=6.1.0 <6.2.6
- PyPI: `proteus` — affected >=5.0.0 <5.0.12
- PyPI: `proteus` — affected >=6.0.0 <6.0.5
- PyPI: `proteus` — affected >=6.1.0 <6.2.2

## Details
An XXE issue was discovered in Tryton Application Platform (Server) 5.x through 5.0.45, 6.x through 6.0.15, and 6.1.x and 6.2.x through 6.2.5, and Tryton Application Platform (Command Line Client (proteus)) 5.x through 5.0.11, 6.x through 6.0.4, and 6.1.x and 6.2.x through 6.2.1. An authenticated user can make the server parse a crafted XML SEPA file to access arbitrary files on the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-26661
- https://discuss.tryton.org/t/security-release-for-issue11219-and-issue11244/5059
- https://foss.heptapod.net/tryton/tryton/-/issues/11219
- https://hg.tryton.org/trytond
- https://lists.debian.org/debian-lts-announce/2022/03/msg00016.html
- https://lists.debian.org/debian-lts-announce/2022/03/msg00017.html
- https://www.debian.org/security/2022/dsa-5098
- https://www.debian.org/security/2022/dsa-5099
