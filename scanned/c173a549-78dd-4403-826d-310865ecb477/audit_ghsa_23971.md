# [H] Doctrine Security Misconfiguration Vulnerability

## Summary
Severity: High
Advisory: GHSA-pw5c-xqf2-6xc2
CVE: CVE-2015-5723
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-pw5c-xqf2-6xc2
Type: github-advisory

## Affected
- Packagist: `doctrine/annotations` — affected >=0 <1.2.7
- Packagist: `doctrine/cache` — affected >=1.4.0 <1.4.2
- Packagist: `doctrine/common` — affected >=0 <2.4.3
- Packagist: `doctrine/common` — affected >=2.5.0-stable <2.5.1
- Packagist: `doctrine/orm` — affected >=2.5.0 <2.5.1
- Packagist: `doctrine/mongodb-odm` — affected >=0 <1.0.2
- Packagist: `doctrine/mongodb-odm-bundle` — affected >=0 <3.0.1
- Packagist: `zendframework/zendframework1` — affected >=1.12.0 <1.12.16
- Packagist: `zendframework/zend-cache` — affected >=2.5.0 <2.5.3
- Packagist: `aws/aws-sdk-php` — affected >=3.0.0 <3.2.1
- Packagist: `doctrine/cache` — affected >=1.0.0 <1.3.2
- Packagist: `zendframework/zend-cache` — affected >=2.4.0 <2.4.8
- Packagist: `zendframework/zendframework` — affected >=2.4.0 <2.4.8
- Packagist: `zfcampus/zf-apigility-doctrine` — affected >=1.0.0 <1.0.3

## Details
Doctrine Annotations before 1.2.7, Cache before 1.3.2 and 1.4.x before 1.4.2, Common before 2.4.3 and 2.5.x before 2.5.1, ORM before 2.4.8 or 2.5.x before 2.5.1, MongoDB ODM before 1.0.2, and MongoDB ODM Bundle before 3.0.1 use world-writable permissions for cache directories, which allows local users to execute arbitrary PHP code with additional privileges by leveraging an application with the umask set to 0 and that executes cache entries as code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5723
- https://framework.zend.com/security/advisory/ZF2015-07
- https://github.com/FriendsOfPHP/security-advisories/blob/master/aws/aws-sdk-php/CVE-2015-5723.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/doctrine/cache/CVE-2015-5723.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/doctrine/orm/CVE-2015-5723.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zend-cache/CVE-2015-5723.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework/CVE-2015-5723.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework1/CVE-2015-5723.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zfcampus/zf-apigility-doctrine/CVE-2015-5723.yaml
- https://github.com/aws/aws-sdk-php/releases/tag/3.2.1
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2IUUC7HPN4XE5NNTG4MR76OC662XRZUO
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HPS7A54FQ2CR6PH4NDR6UIYJIRNFXW67
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2IUUC7HPN4XE5NNTG4MR76OC662XRZUO
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HPS7A54FQ2CR6PH4NDR6UIYJIRNFXW67
- https://www.doctrine-project.org/2015/08/31/security_misconfiguration_vulnerability_in_various_doctrine_projects.html
- http://framework.zend.com/security/advisory/ZF2015-07
- http://www.debian.org/security/2015/dsa-3369
- http://www.doctrine-project.org/2015/08/31/security_misconfiguration_vulnerability_in_various_doctrine_projects.html
