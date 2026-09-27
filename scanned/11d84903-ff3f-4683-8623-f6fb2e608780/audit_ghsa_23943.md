# [M] Zend Access Restriction Bypass

## Summary
Severity: Medium
Advisory: GHSA-f6rc-rh43-h8gr
CVE: CVE-2014-8088
CWE: CWE-287
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-f6rc-rh43-h8gr
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework` — affected >=2.0.0 <2.0.99
- Packagist: `zendframework/zendframework` — affected >=2.1.0 <2.1.99
- Packagist: `zendframework/zendframework` — affected >=2.2.0 <2.2.8
- Packagist: `zendframework/zendframework` — affected >=2.3.0 <2.3.3
- Packagist: `zendframework/zendframework1` — affected >=1.12.0 <1.12.9

## Details
The (1) Zend_Ldap class in Zend before 1.12.9 and (2) Zend\Ldap component in Zend 2.x before 2.2.8 and 2.3.x before 2.3.3 allows remote attackers to bypass authentication via a password starting with a null byte, which triggers an unauthenticated bind.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-8088
- https://github.com/zendframework/zendframework/commit/a4222a6c1dc809f0f32fdafcd1ac4d583a075f2f
- https://exchange.xforce.ibmcloud.com/vulnerabilities/97038
- https://framework.zend.com/security/advisory/ZF2014-05
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework/CVE-2014-8088.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework1/CVE-2014-8088.yaml
- https://github.com/zendframework/zendframework
- http://lists.fedoraproject.org/pipermail/package-announce/2014-October/141070.html
- http://lists.fedoraproject.org/pipermail/package-announce/2014-October/141106.html
- http://www.debian.org/security/2015/dsa-3265
- http://www.openwall.com/lists/oss-security/2014/10/10/5
- http://www.oracle.com/technetwork/topics/security/bulletinjan2015-2370101.html
- http://www.securityfocus.com/bid/70378
