# [C] Zend Framework SQL injection vector using null byte for PDO

## Summary
Severity: Critical
Advisory: GHSA-2hvh-c5c2-vj85
CVE: CVE-2015-7695
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-2hvh-c5c2-vj85
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework1` — affected >=0 <1.12.16

## Details
The PDO adapters in Zend Framework before 1.12.16 do not filer null bytes in SQL statements, which allows remote attackers to execute arbitrary SQL commands via a crafted query.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7695
- https://github.com/zendframework/zf1
- http://framework.zend.com/security/advisory/ZF2015-08
- http://www.debian.org/security/2015/dsa-3369
- http://www.openwall.com/lists/oss-security/2015/09/30/6
- http://www.openwall.com/lists/oss-security/2015/09/30/8
- http://www.openwall.com/lists/oss-security/2015/10/11/3
- http://www.securityfocus.com/bid/76784
