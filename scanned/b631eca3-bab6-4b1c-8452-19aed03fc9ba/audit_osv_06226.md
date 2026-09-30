# [C] Heap buffer overflow in finfo_buffer

## Summary
Severity: Critical
Advisory: BIT-libphp-2022-31627
Aliases: BIT-php-2022-31627, BIT-php-min-2022-31627, CVE-2022-31627
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2022-31627
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.1.0 <8.1.8

## Details
In PHP versions 8.1.x below 8.1.8, when fileinfo functions, such as finfo_buffer, due to incorrect patch applied to the third party code from libmagic, incorrect function may be used to free allocated memory, which may lead to heap corruption.

## References
- https://bugs.php.net/bug.php?id=81723
- https://nvd.nist.gov/vuln/detail/CVE-2022-31627
- https://security.gentoo.org/glsa/202209-20
- https://security.netapp.com/advisory/ntap-20220826-0008/
