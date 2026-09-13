# [M] Symfony Access Control Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-89cp-fvcc-hxh7
CVE: CVE-2012-6432
CWE: CWE-284
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-89cp-fvcc-hxh7
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected 2.2-dev
- Packagist: `symfony/symfony` — affected >=2.0.0 <2.0.20
- Packagist: `symfony/symfony` — affected >=2.1.0 <2.1.5

## Details
Symfony 2.0.x before 2.0.20, 2.1.x before 2.1.5, and 2.2-dev, when the internal routes configuration is enabled, allows remote attackers to access arbitrary services via vectors involving a URI beginning with a `/_internal` substring.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-6432
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2012-6432.yaml
- https://github.com/symfony/symfony
- https://symfony.com/blog/security-release-symfony-2-0-20-and-2-1-5-released
- http://symfony.com/blog/security-release-symfony-2-0-20-and-2-1-5-released
