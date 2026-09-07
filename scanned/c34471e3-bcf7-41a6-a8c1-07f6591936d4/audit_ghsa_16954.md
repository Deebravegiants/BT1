# [C] Zend Framework SQL injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-qh9w-r7g5-q939
CVE: CVE-2014-8089
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-23
Source: https://github.com/advisories/GHSA-qh9w-r7g5-q939
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework1` — affected >=1.12.0 <1.12.9
- Packagist: `zendframework/zend-db` — affected >=2.0.0 <2.0.99
- Packagist: `zendframework/zend-db` — affected >=2.1.0 <2.1.99
- Packagist: `zendframework/zend-db` — affected >=2.2.0 <2.2.8
- Packagist: `zendframework/zend-db` — affected >=2.3.0 <2.3.3
- Packagist: `zendframework/zendframework` — affected >=2.0.0 <2.0.99
- Packagist: `zendframework/zendframework` — affected >=2.1.0 <2.1.99
- Packagist: `zendframework/zendframework` — affected >=2.2.0 <2.2.8
- Packagist: `zendframework/zendframework` — affected >=2.3.0 <2.3.3

## Details
SQL injection vulnerability in Zend Framework before 1.12.9, 2.2.x before 2.2.8, and 2.3.x before 2.3.3, when using the sqlsrv PHP extension, allows remote attackers to execute arbitrary SQL commands via a null byte.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-8089
- https://bugzilla.redhat.com/show_bug.cgi?id=1151277
- https://framework.zend.com/security/advisory/ZF2014-06
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zend-db/CVE-2014-8089.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework/CVE-2014-8089.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework1/CVE-2014-8089.yaml
- http://framework.zend.com/security/advisory/ZF2014-06
- http://seclists.org/oss-sec/2014/q4/276
- http://www.securityfocus.com/bid/70011
