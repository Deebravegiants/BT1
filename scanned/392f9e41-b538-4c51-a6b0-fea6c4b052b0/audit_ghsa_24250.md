# [M] Symfony Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-r7p7-qr7p-2rrf
CVE: CVE-2017-16652
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-r7p7-qr7p-2rrf
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected >=2.7.0 <2.7.38
- Packagist: `symfony/symfony` — affected >=2.8.0 <2.8.31
- Packagist: `symfony/symfony` — affected >=3.2.0 <3.2.14
- Packagist: `symfony/symfony` — affected >=3.3.0 <3.3.13
- Packagist: `symfony/security-http` — affected >=2.7.0 <2.7.38
- Packagist: `symfony/security-http` — affected >=2.8.0 <2.8.31
- Packagist: `symfony/security-http` — affected >=3.2.0 <3.2.14
- Packagist: `symfony/security-http` — affected >=3.3.0 <3.3.13
- Packagist: `symfony/security` — affected >=2.7.0 <2.7.38
- Packagist: `symfony/security` — affected >=2.8.0 <2.8.31
- Packagist: `symfony/security` — affected >=3.2.0 <3.2.14
- Packagist: `symfony/security` — affected >=3.3.0 <3.3.13

## Details
An issue was discovered in Symfony 2.7.x before 2.7.38, 2.8.x before 2.8.31, 3.2.x before 3.2.14, and 3.3.x before 3.3.13. `DefaultAuthenticationSuccessHandler` or `DefaultAuthenticationFailureHandler` takes the content of the `_target_path` parameter and generates a redirect response, but no check is performed on the path, which could be an absolute URL to an external domain. This Open redirect vulnerability can be exploited for example to mount effective phishing attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16652
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-http/CVE-2017-16652.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security/CVE-2017-16652.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2017-16652.yaml
- https://github.com/symfony/symfony
- https://lists.debian.org/debian-lts-announce/2019/03/msg00009.html
- https://symfony.com/blog/cve-2017-16652-open-redirect-vulnerability-on-security-handlers
- https://symfony.com/cve-2017-16652
