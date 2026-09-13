# [H] contao/core PHP object injection vulnerability allows for arbitrary code execution

## Summary
Severity: High
Advisory: GHSA-wq43-8r5p-w3mc
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-wq43-8r5p-w3mc
Type: github-advisory

## Affected
- Packagist: `contao/core` — affected >=2.0.0 <2.11.14
- Packagist: `contao/core` — affected >=3.0.0 <3.2.5

## Details
PHP object injection vulnerability was identified in contao/core due to untrusted data being passed to `deserialize()` function.

## References
- https://github.com/contao/core/issues/6695
- https://github.com/contao/core/commit/d67c46c1f1283134e3050244cfdda0ef26fa5cd4
- https://github.com/contao/core/commit/f939b5be8a0048ef779def3289e2072febef1b37
- https://contao.org/en/news/major-security-hole-found-in-contao.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/core/2014-02-13.yaml
