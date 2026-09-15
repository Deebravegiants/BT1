# [C] heap-buffer-overflow in phar_extract_file

## Summary
Severity: Critical
Advisory: BIT-libphp-2020-7061
Aliases: BIT-php-2020-7061, BIT-php-min-2020-7061, CVE-2020-7061
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2020-7061
Type: osv

## Affected
- Bitnami: `libphp` — affected >=7.4.0 <7.4.3

## Details
In PHP versions 7.3.x below 7.3.15 and 7.4.x below 7.4.3, while extracting PHAR files on Windows using phar extension, certain content inside PHAR file could lead to one-byte read past the allocated buffer. This could potentially lead to information disclosure or crash.

## References
- https://bugs.php.net/bug.php?id=79171
- https://nvd.nist.gov/vuln/detail/CVE-2020-7061
- https://security.gentoo.org/glsa/202003-57
- https://www.tenable.com/security/tns-2021-14
