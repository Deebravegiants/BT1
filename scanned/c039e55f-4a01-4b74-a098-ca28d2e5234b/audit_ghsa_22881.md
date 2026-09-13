# [H] GeSHi vulnerable to Directory Traversal

## Summary
Severity: High
Advisory: GHSA-fw3x-2pr2-5j64
CVE: CVE-2012-3521
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-fw3x-2pr2-5j64
Type: github-advisory

## Affected
- Packagist: `geshi/geshi` — affected >=0 <1.0.8.11

## Details
Multiple directory traversal vulnerabilities in the cssgen contrib module in GeSHi before 1.0.8.11 allow remote attackers to read arbitrary files via a .. (dot dot) in the (1) geshi-path or (2) geshi-lang-path parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-3521
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=685324
- https://github.com/GeSHi/geshi-1.0
- http://lists.fedoraproject.org/pipermail/package-announce/2013-May/105247.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-May/105273.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-May/105317.html
- http://sourceforge.net/p/geshi/code/2507
- http://www.openwall.com/lists/oss-security/2012/08/21/11
