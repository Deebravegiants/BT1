# [C] Symfony Authentication Bypass

## Summary
Severity: Critical
Advisory: GHSA-wvj5-r78r-hhfq
CVE: CVE-2016-2403
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-wvj5-r78r-hhfq
Type: github-advisory

## Affected
- Packagist: `symfony/security-core` — affected >=2.8.0 <2.8.6
- Packagist: `symfony/security-core` — affected >=3.0.0 <3.0.6
- Packagist: `symfony/security` — affected >=2.8.0 <2.8.6
- Packagist: `symfony/security` — affected >=3.0.0 <3.0.6
- Packagist: `symfony/symfony` — affected >=2.8.0 <2.8.6
- Packagist: `symfony/symfony` — affected >=3.0.0 <3.0.6

## Details
Symfony before 2.8.6 and 3.x before 3.0.6 allows remote attackers to bypass authentication by logging in with an empty password and valid username, which triggers an unauthenticated bind.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2403
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-core/CVE-2016-2403.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security/CVE-2016-2403.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2016-2403.yaml
- https://symfony.com/cve-2016-2403
- https://web.archive.org/web/20210123224944/http://www.securityfocus.com/bid/96137
- https://www.debian.org/security/2018/dsa-4262
- http://symfony.com/blog/cve-2016-2403-unauthorized-access-on-a-misconfigured-ldap-server-when-using-an-empty-password
