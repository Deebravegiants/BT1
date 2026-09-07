# [M] Symfony potential Cross-site Scripting vulnerabilities in CodeExtension filters

## Summary
Severity: Medium
Advisory: GHSA-q847-2q57-wmr3
CVE: CVE-2023-46734
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-11-12
Source: https://github.com/advisories/GHSA-q847-2q57-wmr3
Type: github-advisory

## Affected
- Packagist: `symfony/twig-bridge` — affected >=2.0.0 <4.4.51
- Packagist: `symfony/twig-bridge` — affected >=5.0.0 <5.4.31
- Packagist: `symfony/twig-bridge` — affected >=6.0.0 <6.3.8
- Packagist: `symfony/symfony` — affected >=2.0.0 <4.4.51
- Packagist: `symfony/symfony` — affected >=5.0.0 <5.4.31
- Packagist: `symfony/symfony` — affected >=6.0.0 <6.3.8

## Details
### Description

Some Twig filters in CodeExtension use "is_safe=html" but don't actually ensure their input is safe.

### Resolution

Symfony now escapes the output of the affected filters.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/9da9a145ce57e4585031ad4bee37c497353eec7c) for branch 4.4.

### Credits

We would like to thank Pierre Rudloff for reporting the issue and to Nicolas Grekas for providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-q847-2q57-wmr3
- https://nvd.nist.gov/vuln/detail/CVE-2023-46734
- https://github.com/symfony/symfony/commit/5d095d5feb1322b16450284a04d6bb48d1198f54
- https://github.com/symfony/symfony/commit/9da9a145ce57e4585031ad4bee37c497353eec7c
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2023-46734.yaml
- https://github.com/symfony/symfony
- https://lists.debian.org/debian-lts-announce/2023/11/msg00019.html
- https://symfony.com/cve-2023-46734
