# [M] ALPINE-CVE-2026-14663

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-14663
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-14663
Type: osv

## Affected
- Alpine:v3.21: `postgresql16` — affected >=0 <16.15-r0
- Alpine:v3.22: `postgresql16` — affected >=0 <16.15-r0
- Alpine:v3.21: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.22: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.23: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.24: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.23: `postgresql18` — affected >=0 <18.5-r0
- Alpine:v3.24: `postgresql18` — affected >=0 <18.5-r0

## Details
Cleartext storage in PostgreSQL pgcrypto disabled ciphers allows a user to recover cleartext, via direct observation of the faulty ciphertext.  The OpenSSL version and OpenSSL configuration determine the disabled ciphers.  If the application accepts encrypted data as input, decryption will succeed even with the wrong key.  This in turn loses the modest protection from the Modification Detection Code (MDC).  Affected functions are pgp_sym_encrypt, pgp_sym_decrypt, pgp_pub_encrypt, pgp_pub_decrypt, pgp_sym_encrypt_bytea, pgp_sym_decrypt_bytea, pgp_pub_encrypt_bytea, and pgp_pub_decrypt_bytea.  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-14663
