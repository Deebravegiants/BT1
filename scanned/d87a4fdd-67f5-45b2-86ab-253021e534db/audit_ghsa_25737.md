# [H] XML Entity Expansion in trytond and proteus

## Summary
Severity: High
Advisory: GHSA-pm3h-mm62-pwm8
CVE: CVE-2022-26662
CWE: CWE-776
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-03-11
Source: https://github.com/advisories/GHSA-pm3h-mm62-pwm8
Type: github-advisory

## Affected
- PyPI: `trytond` — affected >=5.0.0 <5.0.46
- PyPI: `trytond` — affected >=6.0.0 <6.0.16
- PyPI: `trytond` — affected >=6.1.0 <6.2.6
- PyPI: `proteus` — affected >=5.0.0 <5.0.12
- PyPI: `proteus` — affected >=6.0.0 <6.0.5
- PyPI: `proteus` — affected >=6.1.0 <6.2.2

## Details
An XML Entity Expansion (XEE) issue was discovered in Tryton Application Platform (Server) 5.x through 5.0.45, 6.x through 6.0.15, and 6.1.x and 6.2.x through 6.2.5, and Tryton Application Platform (Command Line Client (proteus)) 5.x through 5.0.11, 6.x through 6.0.4, and 6.1.x and 6.2.x through 6.2.1. An unauthenticated user can send a crafted XML-RPC message to consume all the resources of the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-26662
- https://bugs.tryton.org/issue11244
- https://discuss.tryton.org/t/security-release-for-issue11219-and-issue11244/5059
- https://hg.tryton.org/trytond
- https://lists.debian.org/debian-lts-announce/2022/03/msg00016.html
- https://lists.debian.org/debian-lts-announce/2022/03/msg00017.html
- https://www.debian.org/security/2022/dsa-5098
- https://www.debian.org/security/2022/dsa-5099
