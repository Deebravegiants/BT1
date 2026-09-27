# [H] Zend Framework Information Disclosure

## Summary
Severity: High
Advisory: GHSA-pm9m-w23q-5967
CVE: CVE-2015-7503
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-pm9m-w23q-5967
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework` — affected >=2.5.0 <2.5.2
- Packagist: `zendframework/zend-crypt` — affected >=2.0.0 <2.4.9
- Packagist: `zendframework/zend-crypt` — affected >=2.5.0 <2.5.2
- Packagist: `zendframework/zendframework` — affected >=2.0.0 <2.4.9

## Details
Zend Framework before 2.4.9, zend-framework/zend-crypt 2.4.x before 2.4.9, and 2.5.x before 2.5.2 allows remote attackers to recover the RSA private key.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7503
- https://bugzilla.redhat.com/show_bug.cgi?id=1283137
- https://framework.zend.com/security/advisory/ZF2015-10
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zend-crypt/CVE-2015-7503.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework/CVE-2015-7503.yaml
- https://github.com/zendframework/zendframework
