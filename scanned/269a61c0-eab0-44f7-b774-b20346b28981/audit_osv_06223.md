# [C] UAF due to php_filter_float() failing

## Summary
Severity: Critical
Advisory: BIT-libphp-2021-21708
Aliases: BIT-php-2021-21708, BIT-php-min-2021-21708, CVE-2021-21708
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2021-21708
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.1.0 <8.1.3

## Details
In PHP versions 7.4.x below 7.4.28, 8.0.x below 8.0.16, and 8.1.x below 8.1.3, when using filter functions with FILTER_VALIDATE_FLOAT filter and min/max limits, if the filter fails, there is a possibility to trigger use of allocated memory after free, which can result it crashes, and potentially in overwrite of other memory chunks and RCE. This issue affects: code that uses FILTER_VALIDATE_FLOAT with min/max limits.

## References
- https://bugs.php.net/bug.php?id=81708
- https://nvd.nist.gov/vuln/detail/CVE-2021-21708
- https://security.gentoo.org/glsa/202209-20
- https://security.netapp.com/advisory/ntap-20220325-0004/
