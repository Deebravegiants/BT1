# [C] Symfony Authentication Bypass

## Summary
Severity: Critical
Advisory: GHSA-35c5-28pg-2qg4
CVE: CVE-2018-11407
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-35c5-28pg-2qg4
Type: github-advisory

## Affected
- Packagist: `symfony/security-core` — affected >=2.8.0 <2.8.37
- Packagist: `symfony/security-core` — affected >=3.0.0 <3.3.17
- Packagist: `symfony/security-core` — affected >=3.4.0 <3.4.7
- Packagist: `symfony/security-core` — affected >=4.0.0 <4.0.7
- Packagist: `symfony/security` — affected >=2.8.0 <2.8.37
- Packagist: `symfony/security` — affected >=3.0.0 <3.3.17
- Packagist: `symfony/security` — affected >=3.4.0 <3.4.7
- Packagist: `symfony/security` — affected >=4.0.0 <4.0.7
- Packagist: `symfony/symfony` — affected >=2.8.0 <2.8.37
- Packagist: `symfony/symfony` — affected >=3.0.0 <3.3.17
- Packagist: `symfony/symfony` — affected >=3.4.0 <3.4.7
- Packagist: `symfony/symfony` — affected >=4.0.0 <4.0.7

## Details
An issue was discovered in the LDAP component in Symfony 2.8.x before 2.8.37, 3.3.x before 3.3.17, 3.4.x before 3.4.7, and 4.0.x before 4.0.7. It allows remote attackers to bypass authentication by logging in with a "null" password and valid username, which triggers an unauthenticated bind.  **NOTE:** this issue exists because of an incomplete fix for CVE-2016-2403.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11407
- https://github.com/symfony/symfony/pull/27377
- https://github.com/symfony/symfony/commit/b46fc93785d37ffa5d706a82cd175b33ce8f2934
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-core/CVE-2018-11407.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security/CVE-2018-11407.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2018-11407.yaml
- https://github.com/symfony/symfony
- https://symfony.com/blog/cve-2018-11407-unauthorized-access-on-a-misconfigured-ldap-server-when-using-an-empty-password
- https://symfony.com/cve-2018-11407
