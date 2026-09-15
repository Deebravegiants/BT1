# [C] Reference counting in php_request_shutdown causes Use-After-Free

## Summary
Severity: Critical
Advisory: BIT-libphp-2024-11235
Aliases: BIT-php-2024-11235, BIT-php-min-2024-11235, CVE-2024-11235, GHSA-rwp7-7vc6-8477
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2024-11235
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.4.0 <8.4.5

## Details
In PHP versions 8.3.* before 8.3.19 and 8.4.* before 8.4.5, a code sequence involving __set handler or ??=  operator and exceptions can lead to a use-after-free vulnerability. If the third party can control the memory layout leading to this, for example by supplying specially crafted inputs to the script, it could lead to remote code execution.

## References
- https://github.com/php/php-src/security/advisories/GHSA-rwp7-7vc6-8477
- https://nvd.nist.gov/vuln/detail/CVE-2024-11235
