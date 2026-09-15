# [M] User enumeration leak using switch user functionality in Symfony

## Summary
Severity: Medium
Advisory: GHSA-4vpc-5jx4-cfqg
CVE: CVE-2019-18886
CWE: CWE-200, CWE-203
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-12-02
Source: https://github.com/advisories/GHSA-4vpc-5jx4-cfqg
Type: github-advisory

## Affected
- Packagist: `symfony/security-http` — affected >=4.1.0 <4.2.12
- Packagist: `symfony/security-http` — affected >=4.3.0 <4.3.8
- Packagist: `symfony/symfony` — affected >=4.1.0 <4.2.12
- Packagist: `symfony/symfony` — affected >=4.3.0 <4.3.8

## Details
An issue was discovered in Symfony 4.2.0 to 4.2.11 and 4.3.0 to 4.3.7. The ability to enumerate users was possible due to different handling depending on whether the user existed when making unauthorized attempts to use the switch users functionality. This is related to symfony/security.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18886
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-http/CVE-2019-18886.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2019-18886.yaml
- https://github.com/symfony/symfony/releases/tag/v4.3.8
- https://symfony.com/blog/cve-2019-18886-prevent-user-enumeration-using-switch-user-functionality
- https://symfony.com/blog/symfony-4-3-8-released
- https://symfony.com/cve-2019-18886
