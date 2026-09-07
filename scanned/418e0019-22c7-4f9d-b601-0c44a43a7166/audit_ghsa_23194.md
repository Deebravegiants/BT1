# [M] Symfony Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-7hwc-2cq4-6x2w
CVE: CVE-2018-11408
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-7hwc-2cq4-6x2w
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected >=2.7.0 <2.7.48
- Packagist: `symfony/symfony` — affected >=2.8.0 <2.8.41
- Packagist: `symfony/symfony` — affected >=3.3.0 <3.3.17
- Packagist: `symfony/symfony` — affected >=3.4.0 <3.4.11
- Packagist: `symfony/symfony` — affected >=4.0.0 <4.0.11
- Packagist: `symfony/security-bundle` — affected >=2.7.0 <2.7.48
- Packagist: `symfony/security-bundle` — affected >=2.8.0 <2.8.41
- Packagist: `symfony/security-bundle` — affected >=3.3.0 <3.3.17
- Packagist: `symfony/security-bundle` — affected >=3.4.0 <3.4.11
- Packagist: `symfony/security-bundle` — affected >=4.0.0 <4.0.11

## Details
The security handlers in the Security component in Symfony in 2.7.x before 2.7.48, 2.8.x before 2.8.41, 3.3.x before 3.3.17, 3.4.x before 3.4.11, and 4.0.x before 4.0.11 have an Open redirect vulnerability when security.http_utils is inlined by a container.  NOTE: this issue exists because of an incomplete fix for CVE-2017-16652.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11408
- https://github.com/symfony/symfony/commit/b20e83562e32c56f8d9b8296ab07b0e4c0a54db8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-bundle/CVE-2018-11408.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2018-11408.yaml
- https://github.com/symfony/symfony
- https://lists.debian.org/debian-lts-announce/2019/03/msg00009.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/G4XNBMFW33H47O5TZGA7JYCVLDBCXAJV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UBQK7JDXIELADIPGZIOUCZKMAJM5LSBW
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WU5N2TZFNGXDGMXMPP7LZCWTFLENF6WH
- https://symfony.com/blog/cve-2018-11408-open-redirect-vulnerability-on-security-handlers
- https://symfony.com/cve-2018-11408
