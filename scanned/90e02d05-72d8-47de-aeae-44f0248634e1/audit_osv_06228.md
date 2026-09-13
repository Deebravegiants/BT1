# [M] $_COOKIE names string replacement (. -> _): cookie integrity vulnerabilities

## Summary
Severity: Medium
Advisory: BIT-libphp-2022-31629
Aliases: BIT-php-2022-31629, BIT-php-min-2022-31629, CVE-2022-31629
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2022-31629
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.1.0 <8.1.11

## Details
In PHP versions before 7.4.31, 8.0.24 and 8.1.11, the vulnerability enables network and same-site attackers to set a standard insecure cookie in the victim's browser which is treated as a `__Host-` or `__Secure-` cookie by PHP applications.

## References
- http://www.openwall.com/lists/oss-security/2024/04/12/11
- https://bugs.php.net/bug.php?id=81727
- https://lists.debian.org/debian-lts-announce/2022/12/msg00030.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2L5SUVYGAKSWODUQPZFBUB3AL6E6CSEV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KJZK3X6B7FBE32FETDSMRLJXTFTHKWSY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LSJVPJTX7T3J5V7XHR4MFNHZGP44R5XE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VI3E6A3ZTH2RP7OMLJHSVFIEQBIFM6RF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XNIEABBH5XCXLFWWZYIDE457SPEDZTXV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZGWIK3HMBACERGB4TSBB2JUOMPYY2VKY/
- https://nvd.nist.gov/vuln/detail/CVE-2022-31629
- https://security.gentoo.org/glsa/202211-03
- https://security.netapp.com/advisory/ntap-20221209-0001/
- https://www.debian.org/security/2022/dsa-5277
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KJZK3X6B7FBE32FETDSMRLJXTFTHKWSY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZGWIK3HMBACERGB4TSBB2JUOMPYY2VKY/
