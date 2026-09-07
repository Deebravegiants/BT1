# [M] Symfony allows changing the environment through a query

## Summary
Severity: Medium
Advisory: GHSA-x8vp-gf4q-mw5j
CVE: CVE-2024-50340
CWE: CWE-20, CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-11-06
Source: https://github.com/advisories/GHSA-x8vp-gf4q-mw5j
Type: github-advisory

## Affected
- Packagist: `symfony/runtime` — affected >=5.3.0 <5.4.46
- Packagist: `symfony/runtime` — affected >=6.0.0 <6.4.14
- Packagist: `symfony/runtime` — affected >=7.0.0 <7.1.7
- Packagist: `symfony/symfony` — affected >=5.3.0 <5.4.46
- Packagist: `symfony/symfony` — affected >=6.0.0 <6.4.14
- Packagist: `symfony/symfony` — affected >=7.0.0 <7.1.7

## Details
### Description

When the `register_argc_argv` php directive is set to `on` , and users call any URL with a special crafted query string, they are able to change the environment or debug mode used by the kernel when handling the request.

### Resolution

The `SymfonyRuntime` now ignores the `argv` values for non-cli SAPIs PHP runtimes

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/a77b308c3f179ed7c8a8bc295f82b2d6ee3493fa) for branch 5.4.

### Credits

We would like to thank Vladimir Dusheyko for reporting the issue and Wouter de Jong for providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-x8vp-gf4q-mw5j
- https://nvd.nist.gov/vuln/detail/CVE-2024-50340
- https://github.com/symfony/symfony/commit/a77b308c3f179ed7c8a8bc295f82b2d6ee3493fa
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/runtime/CVE-2024-50340.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2024-50340.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2024-50340
