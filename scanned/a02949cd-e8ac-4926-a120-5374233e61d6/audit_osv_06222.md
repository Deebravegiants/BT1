# [M] Special characters break path parsing in XML functions

## Summary
Severity: Medium
Advisory: BIT-libphp-2021-21707
Aliases: BIT-php-2021-21707, BIT-php-min-2021-21707, CVE-2021-21707
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2021-21707
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.0.0 <8.0.13

## Details
In PHP versions 7.3.x below 7.3.33, 7.4.x below 7.4.26 and 8.0.x below 8.0.13, certain XML parsing functions, like simplexml_load_file(), URL-decode the filename passed to them. If that filename contains URL-encoded NUL character, this may cause the function to interpret this as the end of the filename, thus interpreting the filename differently from what the user intended, which may lead it to reading a different file than intended.

## References
- https://bugs.php.net/bug.php?id=79971
- https://lists.debian.org/debian-lts-announce/2022/12/msg00030.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-21707
- https://security.netapp.com/advisory/ntap-20211223-0005/
- https://www.debian.org/security/2022/dsa-5082
- https://www.tenable.com/security/tns-2022-09
