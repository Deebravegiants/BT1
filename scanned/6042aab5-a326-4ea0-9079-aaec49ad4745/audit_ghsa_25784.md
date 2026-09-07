# [H] Symfony Http-Kernel has non-constant time comparison in UriSigner

## Summary
Severity: High
Advisory: GHSA-q8hg-pf8v-cxrv
CVE: CVE-2019-18887
CWE: CWE-203
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-26
Source: https://github.com/advisories/GHSA-q8hg-pf8v-cxrv
Type: github-advisory

## Affected
- Packagist: `symfony/http-kernel` — affected >=2.2.0 <2.8.52
- Packagist: `symfony/http-kernel` — affected >=3.0.0 <3.4.35
- Packagist: `symfony/http-kernel` — affected >=4.0.0 <4.2.12
- Packagist: `symfony/http-kernel` — affected >=4.3.0 <4.3.8
- Packagist: `symfony/symfony` — affected >=2.2.0 <2.8.52
- Packagist: `symfony/symfony` — affected >=3.0.0 <3.4.35
- Packagist: `symfony/symfony` — affected >=4.0.0 <4.2.12
- Packagist: `symfony/symfony` — affected >=4.3.0 <4.3.8

## Details
When checking the signature of an URI (an ESI fragment URL for instance), the URISigner did not used a constant time string comparison function, resulting in a potential remote timing attack vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18887
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/http-kernel/CVE-2019-18887.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2019-18887.yaml
- https://github.com/symfony/symfony/releases/tag/v4.3.8
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DZNXRVHDQBNZQUCNRVZICPPBFRAUWUJX
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UED22BOXTL2SSFMGYKA64ZFHGLLJG3EA
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VXEAOEANNIVYANTMOJ42NKSU6BGNBULZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DZNXRVHDQBNZQUCNRVZICPPBFRAUWUJX
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UED22BOXTL2SSFMGYKA64ZFHGLLJG3EA
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VXEAOEANNIVYANTMOJ42NKSU6BGNBULZ
- https://symfony.com/blog/cve-2019-18887-use-constant-time-comparison-in-urisigner
- https://symfony.com/blog/symfony-4-3-8-released
- https://symfony.com/cve-2019-18887
