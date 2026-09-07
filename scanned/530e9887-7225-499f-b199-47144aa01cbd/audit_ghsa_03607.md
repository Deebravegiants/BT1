# [C] Invalid HTTP method overrides allow possible XSS or other attacks in Symfony

## Summary
Severity: Critical
Advisory: GHSA-x92h-wmg2-6hp7
CVE: CVE-2019-10913
CWE: CWE-79, CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-12-02
Source: https://github.com/advisories/GHSA-x92h-wmg2-6hp7
Type: github-advisory

## Affected
- Packagist: `symfony/http-foundation` — affected >=2.7.0 <2.7.51
- Packagist: `symfony/http-foundation` — affected >=2.8.0 <2.8.50
- Packagist: `symfony/http-foundation` — affected >=3.0.0 <3.4.26
- Packagist: `symfony/http-foundation` — affected >=4.0.0 <4.1.12
- Packagist: `symfony/http-foundation` — affected >=4.2.0 <4.2.7
- Packagist: `symfony/symfony` — affected >=2.7.0 <2.7.51
- Packagist: `symfony/symfony` — affected >=2.8.0 <2.8.50
- Packagist: `symfony/symfony` — affected >=3.0.0 <3.4.26
- Packagist: `symfony/symfony` — affected >=4.0.0 <4.1.12
- Packagist: `symfony/symfony` — affected >=4.2.0 <4.2.7

## Details
In Symfony before 2.7.51, 2.8.x before 2.8.50, 3.x before 3.4.26, 4.x before 4.1.12, and 4.2.x before 4.2.7, HTTP Methods provided as verbs or using the override header may be treated as trusted input, but they are not validated, possibly causing SQL injection or XSS. This is related to symfony/http-foundation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10913
- https://github.com/symfony/symfony/commit/944e60f083c3bffbc6a0b5112db127a10a66a8ec
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/http-foundation/CVE-2019-10913.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2019-10913.yaml
- https://symfony.com/blog/cve-2019-10913-reject-invalid-http-method-overrides
- https://symfony.com/cve-2019-10913
