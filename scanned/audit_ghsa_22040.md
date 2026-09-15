# [M] Symfony Denial of Service Via Long Password Hashing

## Summary
Severity: Medium
Advisory: GHSA-cr49-fx2v-9p57
CVE: CVE-2013-5958
CWE: CWE-789
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-cr49-fx2v-9p57
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected >=2.0.0 <2.0.25
- Packagist: `symfony/symfony` — affected >=2.1.0 <2.1.13
- Packagist: `symfony/symfony` — affected >=2.2.0 <2.2.9
- Packagist: `symfony/symfony` — affected >=2.3.0 <2.3.6
- Packagist: `symfony/polyfill` — affected >=1.0.0 <1.10.0
- Packagist: `symfony/security` — affected >=2.0.0 <2.0.25
- Packagist: `symfony/security` — affected >=2.1.0 <2.1.13
- Packagist: `symfony/security` — affected >=2.2.0 <2.2.9
- Packagist: `symfony/security` — affected >=2.3.0 <2.3.6

## Details
The Security component in Symfony 2.0.x before 2.0.25, 2.1.x before 2.1.13, 2.2.x before 2.2.9, and 2.3.x before 2.3.6 allows remote attackers to cause a denial of service (CPU consumption) via a long password that triggers an expensive hash computation, as demonstrated by a PBKDF2 computation, a similar issue to CVE-2013-5750.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-5958
- https://github.com/symfony/symfony/issues/11522
- https://github.com/symfony/polyfill/pull/155
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/polyfill/CVE-2013-5958.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security/CVE-2013-5958.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2013-5958.yaml
- https://github.com/symfony/symfony
- https://symfony.com/blog/security-releases-cve-2013-5958-symfony-2-0-25-2-1-13-2-2-9-and-2-3-6-released
- http://symfony.com/blog/security-releases-cve-2013-5958-symfony-2-0-25-2-1-13-2-2-9-and-2-3-6-released
