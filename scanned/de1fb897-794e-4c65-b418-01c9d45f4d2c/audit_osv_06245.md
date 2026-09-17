# [H] PHP mb_encode_mimeheader runs endlessly for some inputs

## Summary
Severity: High
Advisory: BIT-libphp-2024-2757
Aliases: BIT-php-2024-2757, BIT-php-min-2024-2757, CVE-2024-2757, GHSA-fjp9-9hwx-59fq
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2024-2757
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.3.0 <8.3.5

## Details
In PHP 8.3.* before 8.3.5, function mb_encode_mimeheader() runs endlessly for some inputs that contain long strings of non-space characters followed by a space. This could lead to a potential DoS attack if a hostile user sends data to an application that uses this function.

## References
- http://www.openwall.com/lists/oss-security/2024/04/12/11
- https://github.com/php/php-src/security/advisories/GHSA-fjp9-9hwx-59fq
- https://nvd.nist.gov/vuln/detail/CVE-2024-2757
- https://security.netapp.com/advisory/ntap-20240510-0011/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KJZK3X6B7FBE32FETDSMRLJXTFTHKWSY/
