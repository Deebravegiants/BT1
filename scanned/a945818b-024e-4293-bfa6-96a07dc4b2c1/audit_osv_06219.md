# [M] Multiple vulnerabilities in Firebird client extension

## Summary
Severity: Medium
Advisory: BIT-libphp-2021-21704
Aliases: BIT-php-2021-21704, BIT-php-min-2021-21704, CVE-2021-21704
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2021-21704
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.0.0 <8.0.8

## Details
In PHP versions 7.3.x below 7.3.29, 7.4.x below 7.4.21 and 8.0.x below 8.0.8, when using Firebird PDO driver extension, a malicious database server could cause crashes in various database functions, such as getAttribute(), execute(), fetch() and others by returning invalid response data that is not parsed correctly by the driver. This can result in crashes, denial of service or potentially memory corruption.

## References
- https://bugs.php.net/bug.php?id=76448
- https://bugs.php.net/bug.php?id=76449
- https://bugs.php.net/bug.php?id=76450
- https://bugs.php.net/bug.php?id=76452
- https://nvd.nist.gov/vuln/detail/CVE-2021-21704
- https://security.gentoo.org/glsa/202209-20
- https://security.netapp.com/advisory/ntap-20211029-0006/
