# [M] Zend Framework XEE Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jh4x-4wmf-67pr
CVE: CVE-2012-6532
CWE: CWE-776
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-jh4x-4wmf-67pr
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework1` — affected >=1.0 <1.11.13
- Packagist: `zendframework/zendframework1` — affected >=1.12.0-rc1 <1.12.0

## Details
(1) `Zend_Dom`, (2) `Zend_Feed`, (3) `Zend_Soap`, and (4) `Zend_XmlRpc` in Zend Framework 1.x before 1.11.13 and 1.12.x before 1.12.0 allow remote attackers to cause a denial of service (CPU consumption) via recursive or circular references in an XML entity definition in an XML DOCTYPE declaration, aka an XML Entity Expansion (XEE) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-6532
- https://github.com/zendframework/zf1/commit/1b5e86183a72b7b10b6c89e4f95f08c5da9716db
- https://github.com/zendframework/zf1
- https://web.archive.org/web/20131101014013/http://www.mandriva.com/en/support/security/advisories/advisory/MDVSA-2013:115/?name=MDVSA-2013:115
- http://framework.zend.com/security/advisory/ZF2012-02
