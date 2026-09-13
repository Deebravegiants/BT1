# [H] Symfony CSRF Token Fixation

## Summary
Severity: High
Advisory: GHSA-g4g7-q726-v5hg
CVE: CVE-2018-11406
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-g4g7-q726-v5hg
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected >=2.7.0 <2.7.48
- Packagist: `symfony/symfony` — affected >=2.8.0 <2.8.41
- Packagist: `symfony/symfony` — affected >=3.0.0 <3.3.17
- Packagist: `symfony/symfony` — affected >=3.4.0 <3.4.11
- Packagist: `symfony/symfony` — affected >=4.0.0 <4.0.11
- Packagist: `symfony/security-bundle` — affected >=2.7.0 <2.7.48
- Packagist: `symfony/security-bundle` — affected >=2.8.0 <2.8.41
- Packagist: `symfony/security-bundle` — affected >=3.0.0 <3.3.17
- Packagist: `symfony/security-bundle` — affected >=3.4.0 <3.4.11
- Packagist: `symfony/security-bundle` — affected >=4.0.0 <4.0.11
- Packagist: `symfony/security-http` — affected >=2.7.0 <2.7.48
- Packagist: `symfony/security-http` — affected >=2.8.0 <2.8.41
- Packagist: `symfony/security-http` — affected >=3.0.0 <3.3.17
- Packagist: `symfony/security-http` — affected >=3.4.0 <3.4.11
- Packagist: `symfony/security-http` — affected >=4.0.0 <4.0.11
- Packagist: `symfony/security` — affected >=2.7.0 <2.7.48
- Packagist: `symfony/security` — affected >=2.8.0 <2.8.41
- Packagist: `symfony/security` — affected >=3.0.0 <3.3.17
- Packagist: `symfony/security` — affected >=3.4.0 <3.4.11
- Packagist: `symfony/security` — affected >=4.0.0 <4.0.11

## Details
An issue was discovered in the Security component in Symfony 2.7.x before 2.7.48, 2.8.x before 2.8.41, 3.3.x before 3.3.17, 3.4.x before 3.4.11, and 4.0.x before 4.0.11. By default, a user's session is invalidated when the user is logged out. This behavior can be disabled through the invalidate_session option. In this case, CSRF tokens were not erased during logout which allowed for CSRF token fixation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11406
- https://github.com/symfony/symfony/commit/319e1bdd43979d9c1559497de8d69adea28ab8d1
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-bundle/CVE-2018-11406.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-http/CVE-2018-11406.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security/CVE-2018-11406.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2018-11406.yaml
- https://github.com/symfony/symfony
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/G4XNBMFW33H47O5TZGA7JYCVLDBCXAJV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UBQK7JDXIELADIPGZIOUCZKMAJM5LSBW
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WU5N2TZFNGXDGMXMPP7LZCWTFLENF6WH
- https://symfony.com/blog/cve-2018-11406-csrf-token-fixation
- https://symfony.com/cve-2018-11406
- https://www.debian.org/security/2018/dsa-4262
