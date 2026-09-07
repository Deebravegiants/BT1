# [M] Zend Framework XXE Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9m5v-vq4f-mrvf
CVE: CVE-2012-5657
CWE: CWE-200, CWE-611
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9m5v-vq4f-mrvf
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework1` — affected >=0 <1.11.15
- Packagist: `zendframework/zendframework1` — affected >=1.12.0-rc1 <1.12.1

## Details
The (1) Zend_Feed_Rss and (2) Zend_Feed_Atom classes in Zend_Feed in Zend Framework 1.11.x before 1.11.15 and 1.12.x before 1.12.1 allow remote attackers to read arbitrary files, send HTTP requests to intranet servers, and possibly cause a denial of service (CPU and memory consumption) via an XML External Entity (XXE) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5657
- https://github.com/zendframework/zf1/commit/15c84914f063efea49ea1c4425459a792cc185ea
- https://github.com/zendframework/zf1
- https://web.archive.org/web/20131101014013/http://www.mandriva.com/en/support/security/advisories/advisory/MDVSA-2013:115/?name=MDVSA-2013:115
- http://framework.zend.com/security/advisory/ZF2012-05
- http://openwall.com/lists/oss-security/2012/12/20/2
- http://openwall.com/lists/oss-security/2012/12/20/4
- http://www.debian.org/security/2012/dsa-2602
