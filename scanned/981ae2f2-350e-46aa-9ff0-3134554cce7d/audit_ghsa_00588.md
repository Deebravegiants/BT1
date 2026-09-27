# [H] Path Traversal in minsoft:ms-mcms

## Summary
Severity: High
Advisory: GHSA-7hjp-97g3-rq93
CVE: CVE-2018-18831
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-11-01
Source: https://github.com/advisories/GHSA-7hjp-97g3-rq93
Type: github-advisory

## Affected
- Maven: `net.mingsoft:ms-mcms` — affected >=0

## Details
An issue was discovered in com\mingsoft\cms\action\GeneraterAction.java in MCMS 4.6.5. An attacker can write a .jsp file (in the position parameter) to an arbitrary directory via a ../ Directory Traversal in the url parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18831
- https://gitee.com/mingSoft/MCMS/issues/IO0K0
- https://github.com/advisories/GHSA-7hjp-97g3-rq93
