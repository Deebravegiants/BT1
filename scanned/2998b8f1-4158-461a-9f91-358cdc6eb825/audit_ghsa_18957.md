# [H] Symfony's incorrect parsing of PATH_INFO can lead to limited authorization bypass

## Summary
Severity: High
Advisory: GHSA-3rg7-wf37-54rm
CVE: CVE-2025-64500
CWE: CWE-647
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-11-12
Source: https://github.com/advisories/GHSA-3rg7-wf37-54rm
Type: github-advisory

## Affected
- Packagist: `symfony/http-foundation` — affected >=0 <5.4.50
- Packagist: `symfony/http-foundation` — affected >=6.0.0 <6.4.29
- Packagist: `symfony/http-foundation` — affected >=7.0.0 <7.3.7
- Packagist: `symfony/symfony` — affected >=2.0.0 <5.4.50
- Packagist: `symfony/symfony` — affected >=6.0.0 <6.4.29
- Packagist: `symfony/symfony` — affected >=7.0.0 <7.3.7

## Details
### Description

The `Request` class improperly interprets some `PATH_INFO` in a way that leads to representing some URLs with a path that doesn't start with a `/`. This can allow bypassing some access control rules that are built with this `/`-prefix assumption.

### Resolution

The `Request` class now ensures that URL paths always start with a `/`.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/9962b91b12bb791322fa73836b350836b6db7cac) for branch 5.4.

### Credits

We would like to thank Andrew Atkinson for discovering the issue, Chris Smith for reporting it and Nicolas Grekas for providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-3rg7-wf37-54rm
- https://nvd.nist.gov/vuln/detail/CVE-2025-64500
- https://github.com/symfony/symfony/commit/9962b91b12bb791322fa73836b350836b6db7cac
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/http-foundation/CVE-2025-64500.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2025-64500.yaml
- https://github.com/symfony/symfony
- https://symfony.com/blog/cve-2025-64500-incorrect-parsing-of-path-info-can-lead-to-limited-authorization-bypass
