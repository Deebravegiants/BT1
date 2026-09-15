# [M] Improper Restriction of XML External Entity Reference in Openpyxl

## Summary
Severity: Medium
Advisory: GHSA-chqf-hx79-gxc6
CVE: CVE-2017-5992
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-chqf-hx79-gxc6
Type: github-advisory

## Affected
- PyPI: `openpyxl` — affected >=0 <2.4.2

## Details
Openpyxl 2.4.1 resolves external entities by default, which allows remote attackers to conduct XXE attacks via a crafted .xlsx document.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5992
- https://bitbucket.org/openpyxl/openpyxl/commits/3b4905f428e1
- https://bitbucket.org/openpyxl/openpyxl/issues/749
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=854442
- https://foss.heptapod.net/openpyxl/openpyxl
- https://foss.heptapod.net/openpyxl/openpyxl/-/commit/7fe678fd89fd
- https://foss.heptapod.net/openpyxl/openpyxl/-/issues/749
- https://github.com/advisories/GHSA-chqf-hx79-gxc6
- https://github.com/pypa/advisory-database/tree/main/vulns/openpyxl/PYSEC-2017-48.yaml
- http://www.openwall.com/lists/oss-security/2017/02/07/5
