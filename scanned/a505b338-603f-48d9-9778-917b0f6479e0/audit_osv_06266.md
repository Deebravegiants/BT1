# [M] ext/openssl: Memory corruption in openssl_encrypt with AES-WRAP-PAD

## Summary
Severity: Medium
Advisory: BIT-libphp-2026-14355
Aliases: BIT-php-2026-14355, BIT-php-min-2026-14355, CVE-2026-14355
Ecosystem: Bitnami
Published: 2026-07-08
Source: https://osv.dev/vulnerability/BIT-libphp-2026-14355
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.5.0 <8.5.8

## Details
In PHP versions 8.2.* before 8.2.32, 8.3.* before 8.3.32, 8.4.* before 8.4.23, 8.5.* before 8.5.8, the AES-WRAP-PAD algorithm implementation in OpenSSL extension contains a buffer allocation flaw. The output buffer for the AES key-wrap-with-padding operation is sized from the plaintext length without accounting for RFC 5649 expansion. This may cause OpenSSL to write beyond allocated memory, corrupting heap metadata and triggering application abort.

## References
- https://github.com/php/php-src/security/advisories/GHSA-7jrw-539f-x6vr
- https://lists.debian.org/debian-lts-announce/2026/07/msg00010.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-14355
