# [H] Path traversal in bolt/core

## Summary
Severity: High
Advisory: GHSA-q88g-qx42-xfrh
CVE: CVE-2021-27367
CWE: CWE-22
Ecosystem: Packagist
Published: 2021-02-18
Source: https://github.com/advisories/GHSA-q88g-qx42-xfrh
Type: github-advisory

## Affected
- Packagist: `bolt/core` — affected >=0 <4.1.13

## Details
Controller/Backend/FileEditController.php and Controller/Backend/FilemanagerController.php in Bolt before 4.1.13 allow Directory Traversal.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27367
- https://github.com/bolt/core/pull/2371
- https://github.com/bolt/core/releases/tag/4.1.13
- https://packagist.org/packages/bolt/core
