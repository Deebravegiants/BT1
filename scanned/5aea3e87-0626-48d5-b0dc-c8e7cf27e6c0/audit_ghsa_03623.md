# [C] Symfony Unsafe Cache Serialization Could Enable RCE

## Summary
Severity: Critical
Advisory: GHSA-79gr-58r3-pwm3
CVE: CVE-2019-18889
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-12-02
Source: https://github.com/advisories/GHSA-79gr-58r3-pwm3
Type: github-advisory

## Affected
- Packagist: `symfony/cache` — affected >=3.1.0 <3.4.35
- Packagist: `symfony/cache` — affected >=4.0.0 <4.2.12
- Packagist: `symfony/cache` — affected >=4.3.0 <4.3.8
- Packagist: `symfony/symfony` — affected >=3.1.0 <3.4.35
- Packagist: `symfony/symfony` — affected >=4.0.0 <4.2.12
- Packagist: `symfony/symfony` — affected >=4.3.0 <4.3.8

## Details
An issue was discovered in Symfony 3.4.0 through 3.4.34, 4.2.0 through 4.2.11, and 4.3.0 through 4.3.7. Serializing certain cache adapter interfaces could result in remote code injection. This is related to symfony/cache.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18889
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/cache/CVE-2019-18889.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2019-18889.yaml
- https://github.com/symfony/symfony/releases/tag/v4.3.8
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UED22BOXTL2SSFMGYKA64ZFHGLLJG3EA
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UED22BOXTL2SSFMGYKA64ZFHGLLJG3EA
- https://symfony.com/blog/cve-2019-18889-forbid-serializing-abstractadapter-and-tagawareadapter-instances
- https://symfony.com/blog/symfony-4-3-8-released
- https://symfony.com/cve-2019-18889
