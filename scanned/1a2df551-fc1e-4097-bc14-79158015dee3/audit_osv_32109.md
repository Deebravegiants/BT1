# [M] Twig fixes a security issue where escaping was missing when using null coalesce operator (??)

## Summary
Severity: Medium
Advisory: CVE-2025-24374
Aliases: GHSA-3xg3-cgvq-2xwr
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2025-01-29
Source: https://osv.dev/vulnerability/CVE-2025-24374
Type: osv

## Details
Twig is a template language for PHP. When using the ?? operator, output escaping was missing for the expression on the left side of the operator. This vulnerability is fixed in 3.19.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24374.json
- https://github.com/twigphp/Twig/security/advisories/GHSA-3xg3-cgvq-2xwr
- https://nvd.nist.gov/vuln/detail/CVE-2025-24374
- https://github.com/twigphp/Twig/commit/38576b12f05df3cc871bf68f39ccb46b418334a3
