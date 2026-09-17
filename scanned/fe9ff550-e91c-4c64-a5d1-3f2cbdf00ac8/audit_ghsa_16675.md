# [M] Symfony has a security issue when parsing the Authorization header

## Summary
Severity: Medium
Advisory: GHSA-h7v2-2qwg-h829
CVE: CVE-2014-6061
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-h7v2-2qwg-h829
Type: github-advisory

## Affected
- Packagist: `symfony/http-foundation` — affected >=2.0.0 <2.3.19
- Packagist: `symfony/http-foundation` — affected >=2.4.0 <2.4.9
- Packagist: `symfony/http-foundation` — affected >=2.5.0 <2.5.4
- Packagist: `symfony/symfony` — affected >=2.0.0 <2.3.19
- Packagist: `symfony/symfony` — affected >=2.4.0 <2.4.9
- Packagist: `symfony/symfony` — affected >=2.5.0 <2.5.4

## Details
All 2.0.X, 2.1.X, 2.2.X, 2.3.X, 2.4.X, and 2.5.X versions of the Symfony HttpFoundation component are affected by this security issue.

This issue has been fixed in Symfony 2.3.19, 2.4.9, and 2.5.4. Note that no fixes are provided for Symfony 2.0, 2.1, and 2.2 as they are not maintained anymore.

### Description
When an application uses an HTTP basic or digest authentication, Symfony does not parse the `Authorization` header properly, which could be exploited in some server setups (no exploits have been demonstrated though.)

### Resolution
The parsing of the `Authorization` header has been fixed to comply to the HTTP specification.

The patch for this issue is available here: https://github.com/symfony/symfony/pull/11829

## References
- https://github.com/symfony/symfony/pull/11829
- https://github.com/symfony/symfony/commit/3b4046e89467dc1fb5e079e377c2cfd4c239f904
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/http-foundation/CVE-2014-6061.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2014-6061.yaml
- https://symfony.com/cve-2014-6061
