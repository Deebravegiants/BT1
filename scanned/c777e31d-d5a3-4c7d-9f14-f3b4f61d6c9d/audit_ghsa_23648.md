# [H] Symfony Session Fixation Vulnerability

## Summary
Severity: High
Advisory: GHSA-g4rg-rw65-8hfg
CVE: CVE-2018-11385
CWE: CWE-384
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-g4rg-rw65-8hfg
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected >=2.7.0 <2.7.48
- Packagist: `symfony/symfony` — affected >=2.8.0 <2.8.41
- Packagist: `symfony/symfony` — affected >=3.0.0 <3.3.17
- Packagist: `symfony/symfony` — affected >=3.4.0 <3.4.11
- Packagist: `symfony/symfony` — affected >=4.0.0 <4.0.11
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
An issue was discovered in the Security component in Symfony 2.7.x before 2.7.48, 2.8.x before 2.8.41, 3.3.x before 3.3.17, 3.4.x before 3.4.11, and 4.0.x before 4.0.11. A session fixation vulnerability within the "Guard" login feature may allow an attacker to impersonate a victim towards the web application if the session id value was previously known to the attacker.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11385
- https://github.com/symfony/symfony/commit/194caff28b56707ea98e746c6582c06acbb9bc3f
- https://github.com/symfony/symfony/commit/fa5bf4b17d45ee32f41bd1a9abc3fb6c134ec89b
- https://github.com/symfony/symfony/commit/fad1e1f2ea336e85c889feece9d0e23fbfcf777d
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-http/CVE-2018-11385.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security/CVE-2018-11385.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2018-11385.yaml
- https://github.com/symfony/symfony
- https://lists.debian.org/debian-lts-announce/2019/03/msg00009.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/G4XNBMFW33H47O5TZGA7JYCVLDBCXAJV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UBQK7JDXIELADIPGZIOUCZKMAJM5LSBW
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WU5N2TZFNGXDGMXMPP7LZCWTFLENF6WH
- https://symfony.com/blog/cve-2018-11385-session-fixation-issue-for-guard-authentication
- https://symfony.com/cve-2018-11385
- https://www.debian.org/security/2018/dsa-4262
