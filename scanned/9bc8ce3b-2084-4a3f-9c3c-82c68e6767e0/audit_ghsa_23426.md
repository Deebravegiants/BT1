# [C] Contao SQL injection in the backend and listing module

## Summary
Severity: Critical
Advisory: GHSA-w38g-hj45-mjjp
CVE: CVE-2017-16558
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-w38g-hj45-mjjp
Type: github-advisory

## Affected
- Packagist: `contao/contao` — affected >=3.0.0
- Packagist: `contao/contao` — affected >=4.0.0 <4.4.8
- Packagist: `contao/core-bundle` — affected >=4.0.0 <4.4.8
- Packagist: `contao/listing-bundle` — affected >=4.0.0 <4.4.8
- Packagist: `contao/core-bundle` — affected >=3.0.0
- Packagist: `contao/listing-bundle` — affected >=3.0.0

## Details
Contao 3.0.0 to 3.5.30 and 4.0.0 to 4.4.7 contains an SQL injection vulnerability in the backend as well as in the listing module.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16558
- https://github.com/contao/contao/commit/501cb3cd34d61089b94e7ed78da53977bc71fc3e
- https://github.com/contao/contao/commit/6b4a2711edf166c85cfd7a53fed6aea56d4f0544
- https://contao.org/de/changelog/versions/4.4.html
- https://contao.org/en/news/contao-4_4_8.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/contao/CVE-2017-16558.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/core-bundle/CVE-2017-16558.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/listing-bundle/CVE-2017-16558.yaml
- https://github.com/contao/contao/blob/4.4.57/CHANGELOG.md#448-2017-11-15
