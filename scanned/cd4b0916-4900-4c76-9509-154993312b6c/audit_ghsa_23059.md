# [M] Symfony Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-89r2-5g34-2g47
CVE: CVE-2018-19790
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-89r2-5g34-2g47
Type: github-advisory

## Affected
- Packagist: `symfony/security-http` — affected >=2.7.38 <2.7.50
- Packagist: `symfony/security-http` — affected >=2.8.0 <2.8.49
- Packagist: `symfony/security-http` — affected >=3.0.0 <3.4.20
- Packagist: `symfony/security-http` — affected >=4.0.0 <4.0.15
- Packagist: `symfony/security-http` — affected >=4.1.0 <4.1.9
- Packagist: `symfony/security-http` — affected >=4.2.0 <4.2.1
- Packagist: `symfony/security` — affected >=2.7.38 <2.7.50
- Packagist: `symfony/security` — affected >=2.8.0 <2.8.49
- Packagist: `symfony/security` — affected >=3.0.0 <3.4.19
- Packagist: `symfony/security` — affected >=4.0.0 <4.0.15
- Packagist: `symfony/security` — affected >=4.1.0 <4.1.9
- Packagist: `symfony/security` — affected >=4.2.0 <4.2.1
- Packagist: `symfony/symfony` — affected >=2.7.38 <2.7.50
- Packagist: `symfony/symfony` — affected >=2.8.0 <2.8.49
- Packagist: `symfony/symfony` — affected >=3.0.0 <3.4.20
- Packagist: `symfony/symfony` — affected >=4.0.0 <4.0.15
- Packagist: `symfony/symfony` — affected >=4.1.0 <4.1.9

## Details
An open redirect was discovered in Symfony 2.7.x before 2.7.50, 2.8.x before 2.8.49, 3.x before 3.4.20, 4.0.x before 4.0.15, 4.1.x before 4.1.9 and 4.2.x before 4.2.1. By using backslashes in the `_failure_path` input field of login forms, an attacker can work around the redirection target restrictions and effectively redirect the user to any domain after login.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19790
- https://github.com/symfony/symfony/commit/99a0cec0a6be39ce5ef38386e57339603b33ee5b
- https://www.debian.org/security/2019/dsa-4441
- https://web.archive.org/web/20200227095826/http://www.securityfocus.com/bid/106249
- https://symfony.com/cve-2018-19790
- https://symfony.com/blog/cve-2018-19790-open-redirect-vulnerability-when-using-security-http
- https://seclists.org/bugtraq/2019/May/21
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OA4WVFN5FYPIXAPLWZI6N425JHHDSWAZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JZMRJ7VTHCY5AZK24G4QGX36RLUDTDKE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4TD3E7FZIXLVFG3SMFJPDEKPZ26TJOW7
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OA4WVFN5FYPIXAPLWZI6N425JHHDSWAZ
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JZMRJ7VTHCY5AZK24G4QGX36RLUDTDKE
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4TD3E7FZIXLVFG3SMFJPDEKPZ26TJOW7
- https://lists.debian.org/debian-lts-announce/2019/03/msg00009.html
- https://github.com/symfony/symfony
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2018-19790.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security/CVE-2018-19790.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-http/CVE-2018-19790.yaml
- http://www.securityfocus.com/bid/106249
