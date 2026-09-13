# [M] Use of freed hash key in the phar_parse_zipfile function

## Summary
Severity: Medium
Advisory: BIT-libphp-2020-7068
Aliases: BIT-php-2020-7068, BIT-php-min-2020-7068, CVE-2020-7068
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2020-7068
Type: osv

## Affected
- Bitnami: `libphp` — affected >=7.4.0 <7.4.9

## Details
In PHP versions 7.2.x below 7.2.33, 7.3.x below 7.3.21 and 7.4.x below 7.4.9, while processing PHAR files using phar extension, phar_parse_zipfile could be tricked into accessing freed memory, which could lead to a crash or information disclosure.

## References
- https://bugs.php.net/bug.php?id=79797
- https://nvd.nist.gov/vuln/detail/CVE-2020-7068
- https://security.gentoo.org/glsa/202009-10
- https://security.netapp.com/advisory/ntap-20200918-0005/
- https://www.debian.org/security/2021/dsa-4856
- https://www.tenable.com/security/tns-2021-14
