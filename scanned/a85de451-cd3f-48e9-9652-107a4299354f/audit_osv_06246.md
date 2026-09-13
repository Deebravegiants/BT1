# [M] PHP function password_verify can erroneously return true when argument contains NUL

## Summary
Severity: Medium
Advisory: BIT-libphp-2024-3096
Aliases: BIT-php-2024-3096, BIT-php-min-2024-3096, CVE-2024-3096, GHSA-h746-cjrr-wfmr
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2024-3096
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.3.0 <8.3.5

## Details
In PHP  version 8.1.* before 8.1.28, 8.2.* before 8.2.18, 8.3.* before 8.3.5, if a password stored with password_hash() starts with a null byte (\x00), testing a blank string as the password via password_verify() will incorrectly return true.

## References
- http://www.openwall.com/lists/oss-security/2024/04/12/11
- https://github.com/php/php-src/security/advisories/GHSA-h746-cjrr-wfmr
- https://lists.debian.org/debian-lts-announce/2024/05/msg00005.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-3096
- https://security.netapp.com/advisory/ntap-20240510-0010/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KJZK3X6B7FBE32FETDSMRLJXTFTHKWSY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZGWIK3HMBACERGB4TSBB2JUOMPYY2VKY/
