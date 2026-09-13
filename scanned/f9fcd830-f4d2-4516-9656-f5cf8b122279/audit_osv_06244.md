# [M] __Host-/__Secure- cookie bypass due to partial CVE-2022-31629 fix

## Summary
Severity: Medium
Advisory: BIT-libphp-2024-2756
Aliases: BIT-php-2024-2756, BIT-php-min-2024-2756, CVE-2024-2756, GHSA-wpj3-hf5j-x4v4
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2024-2756
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.3.0 <8.3.5

## Details
Due to an incomplete fix to  CVE-2022-31629 https://github.com/advisories/GHSA-c43m-486j-j32p , network and same-site attackers can set a standard insecure cookie in the victim's browser which is treated as a __Host- or __Secure- cookie by PHP applications.

## References
- http://www.openwall.com/lists/oss-security/2024/04/12/11
- https://github.com/php/php-src/security/advisories/GHSA-wpj3-hf5j-x4v4
- https://lists.debian.org/debian-lts-announce/2024/05/msg00005.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-2756
- https://security.netapp.com/advisory/ntap-20240510-0008/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KJZK3X6B7FBE32FETDSMRLJXTFTHKWSY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZGWIK3HMBACERGB4TSBB2JUOMPYY2VKY/
