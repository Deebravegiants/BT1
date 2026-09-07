# [M] Symfony CSRF Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-92x6-h2gr-8gxq
CVE: CVE-2017-16653
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-92x6-h2gr-8gxq
Type: github-advisory

## Affected
- Packagist: `symfony/security-csrf` — affected >=2.7.0 <2.7.38
- Packagist: `symfony/security-csrf` — affected >=2.8.0 <2.8.31
- Packagist: `symfony/security-csrf` — affected >=3.0.0 <3.2.14
- Packagist: `symfony/security-csrf` — affected >=3.3.0 <3.3.13
- Packagist: `symfony/security` — affected >=2.7.0 <2.7.38
- Packagist: `symfony/security` — affected >=2.8.0 <2.8.31
- Packagist: `symfony/security` — affected >=3.0.0 <3.2.14
- Packagist: `symfony/security` — affected >=3.3.0 <3.3.13
- Packagist: `symfony/symfony` — affected >=2.7.0 <2.7.38
- Packagist: `symfony/symfony` — affected >=2.8.0 <2.8.31
- Packagist: `symfony/symfony` — affected >=3.0.0 <3.2.14
- Packagist: `symfony/symfony` — affected >=3.3.0 <3.3.13

## Details
An issue was discovered in Symfony before 2.7.38, 2.8.31, 3.2.14, 3.3.13, 3.4-BETA5, and 4.0-BETA5. The current implementation of CSRF protection in Symfony (Version >=2) does not use different tokens for HTTP and HTTPS; therefore the token is subject to MITM attacks on HTTP and can then be used in an HTTPS context to do CSRF attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16653
- https://github.com/symfony/symfony/pull/24992
- https://github.com/symfony/symfony/commit/b4dbdd7cd8732483d585eacff3428c16b07ad15e
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-csrf/CVE-2017-16653.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security/CVE-2017-16653.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2017-16653.yaml
- https://github.com/symfony/symfony
- https://symfony.com/blog/cve-2017-16653-csrf-protection-does-not-use-different-tokens-for-http-and-https
- https://symfony.com/cve-2017-16653
- https://www.debian.org/security/2018/dsa-4262
