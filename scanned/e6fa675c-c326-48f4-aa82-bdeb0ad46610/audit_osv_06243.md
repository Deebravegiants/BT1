# [M] PHP is vulnerable to the Marvin Attack

## Summary
Severity: Medium
Advisory: BIT-libphp-2024-2408
Aliases: BIT-php-2024-2408, BIT-php-min-2024-2408, CVE-2024-2408, GHSA-hh26-4ppw-5864
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2024-2408
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.3.0 <8.3.8

## Details
The openssl_private_decrypt function in PHP, when using PKCS1 padding (OPENSSL_PKCS1_PADDING, which is the default), is vulnerable to the Marvin Attack unless it is used with an OpenSSL version that includes the changes from this pull request:  https://github.com/openssl/openssl/pull/13817  (rsa_pkcs1_implicit_rejection). These changes are part of OpenSSL 3.2 and have also been backported to stable versions of various Linux distributions, as well as to the PHP builds provided for Windows since the previous release. All distributors and builders should ensure that this version is used to prevent PHP from being vulnerable.

PHP Windows builds for the versions 8.1.29, 8.2.20 and 8.3.8 and above include OpenSSL patches that fix the vulnerability.

## References
- https://github.com/php/php-src/security/advisories/GHSA-hh26-4ppw-5864
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PKGTQUOA2NTZ3RXN22CSAUJPIRUYRB4B/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/W45DBOH56NQDRTOM2DN2LNA2FZIMC3PK/
- https://nvd.nist.gov/vuln/detail/CVE-2024-2408
- https://security.netapp.com/advisory/ntap-20250321-0008/
