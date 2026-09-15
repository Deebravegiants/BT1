# [C] Integer overflow in the firebird and dblib quoters causing OOB writes

## Summary
Severity: Critical
Advisory: BIT-libphp-2024-11236
Aliases: BIT-php-2024-11236, BIT-php-min-2024-11236, CVE-2024-11236, GHSA-5hqh-c84r-qjcv
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2024-11236
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.3.0 <8.3.14

## Details
In PHP versions 8.1.* before 8.1.31, 8.2.* before 8.2.26, 8.3.* before 8.3.14, uncontrolled long string inputs to ldap_escape() function on 32-bit systems can cause an integer overflow, resulting in an out-of-bounds write.

## References
- https://github.com/php/php-src/security/advisories/GHSA-5hqh-c84r-qjcv
- https://nvd.nist.gov/vuln/detail/CVE-2024-11236
- https://lists.debian.org/debian-lts-announce/2024/12/msg00007.html
- https://security.netapp.com/advisory/ntap-20241220-0008/
