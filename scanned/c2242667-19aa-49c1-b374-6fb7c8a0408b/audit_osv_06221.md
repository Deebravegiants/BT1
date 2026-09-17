# [M] ZipArchive::extractTo may extract outside of destination dir

## Summary
Severity: Medium
Advisory: BIT-libphp-2021-21706
Aliases: BIT-php-2021-21706, BIT-php-min-2021-21706, CVE-2021-21706
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2021-21706
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.0.0 <8.0.11

## Details
In PHP versions 7.3.x below 7.3.31, 7.4.x below 7.4.24 and 8.0.x below 8.0.11, in Microsoft Windows environment, ZipArchive::extractTo may be tricked into writing a file outside target directory when extracting a ZIP file, thus potentially causing files to be created or overwritten, subject to OS permissions.

## References
- https://bugs.php.net/bug.php?id=81420
- https://nvd.nist.gov/vuln/detail/CVE-2021-21706
- https://security.netapp.com/advisory/ntap-20211029-0007/
