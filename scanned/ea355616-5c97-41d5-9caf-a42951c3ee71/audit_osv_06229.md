# [H] OOB read due to insufficient input validation in imageloadfont()

## Summary
Severity: High
Advisory: BIT-libphp-2022-31630
Aliases: BIT-php-2022-31630, BIT-php-min-2022-31630, CVE-2022-31630
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2022-31630
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.1.0 <8.1.12

## Details
In PHP versions prior to 7.4.33, 8.0.25 and 8.1.12, when using imageloadfont() function in gd extension, it is possible to supply a specially crafted font file, such as if the loaded font is used with imagechar() function, the read outside allocated buffer will be used. This can lead to crashes or disclosure of confidential information.

## References
- https://bugs.php.net/bug.php?id=81739
- https://nvd.nist.gov/vuln/detail/CVE-2022-31630
