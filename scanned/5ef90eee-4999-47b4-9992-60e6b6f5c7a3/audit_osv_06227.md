# [M] phar wrapper can occur dos when using quine gzip file

## Summary
Severity: Medium
Advisory: BIT-libphp-2022-31628
Aliases: BIT-php-2022-31628, BIT-php-min-2022-31628, CVE-2022-31628
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2022-31628
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.1.0 <8.1.11

## Details
In PHP versions before 7.4.31, 8.0.24 and 8.1.11, the phar uncompressor code would recursively uncompress "quines" gzip files, resulting in an infinite loop.

## References
- https://bugs.php.net/bug.php?id=81726
- https://lists.debian.org/debian-lts-announce/2022/12/msg00030.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2L5SUVYGAKSWODUQPZFBUB3AL6E6CSEV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VI3E6A3ZTH2RP7OMLJHSVFIEQBIFM6RF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XNIEABBH5XCXLFWWZYIDE457SPEDZTXV/
- https://nvd.nist.gov/vuln/detail/CVE-2022-31628
- https://security.gentoo.org/glsa/202211-03
- https://security.netapp.com/advisory/ntap-20221209-0001/
- https://www.debian.org/security/2022/dsa-5277
