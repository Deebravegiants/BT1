# [H] Argument injection in a MimeTypeGuesser in Symfony

## Summary
Severity: High
Advisory: GHSA-xhh6-956q-4q69
CVE: CVE-2019-18888
CWE: CWE-20, CWE-88
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-12-02
Source: https://github.com/advisories/GHSA-xhh6-956q-4q69
Type: github-advisory

## Affected
- Packagist: `symfony/http-foundation` — affected >=2.0.0 <2.8.52
- Packagist: `symfony/http-foundation` — affected >=3.0.0 <3.4.35
- Packagist: `symfony/http-foundation` — affected >=4.0.0 <4.2.12
- Packagist: `symfony/http-foundation` — affected >=4.3.0 <4.3.8
- Packagist: `symfony/mime` — affected >=4.3.0 <4.3.8
- Packagist: `symfony/symfony` — affected >=2.0.0 <2.8.52
- Packagist: `symfony/symfony` — affected >=3.0.0 <3.4.35
- Packagist: `symfony/symfony` — affected >=4.0.0 <4.2.12
- Packagist: `symfony/symfony` — affected >=4.3.0 <4.3.8

## Details
An issue was discovered in Symfony 2.8.0 through 2.8.50, 3.4.0 through 3.4.34, 4.2.0 through 4.2.11, and 4.3.0 through 4.3.7. If an application passes unvalidated user input as the file for which MIME type validation should occur, then arbitrary arguments are passed to the underlying file command. This is related to symfony/http-foundation (and symfony/mime in 4.3.x).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18888
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/http-foundation/CVE-2019-18888.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/mime/CVE-2019-18888.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2019-18888.yaml
- https://github.com/symfony/symfony/releases/tag/v4.3.8
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DZNXRVHDQBNZQUCNRVZICPPBFRAUWUJX
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UED22BOXTL2SSFMGYKA64ZFHGLLJG3EA
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VXEAOEANNIVYANTMOJ42NKSU6BGNBULZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DZNXRVHDQBNZQUCNRVZICPPBFRAUWUJX
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UED22BOXTL2SSFMGYKA64ZFHGLLJG3EA
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VXEAOEANNIVYANTMOJ42NKSU6BGNBULZ
- https://symfony.com/blog/cve-2019-18888-prevent-argument-injection-in-a-mimetypeguesser
- https://symfony.com/blog/symfony-4-3-8-released
- https://symfony.com/cve-2019-18888
