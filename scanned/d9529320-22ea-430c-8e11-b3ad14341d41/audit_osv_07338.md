# [M] PostgreSQL pgcrypto, for OpenSSL-disabled ciphers, silently encrypts to and decrypts from cleartext

## Summary
Severity: Medium
Advisory: BIT-postgresql-2026-14663
Aliases: CVE-2026-14663
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-postgresql-2026-14663
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=18.0.0 <18.5.0

## Details
Cleartext storage in PostgreSQL pgcrypto disabled ciphers allows a user to recover cleartext, via direct observation of the faulty ciphertext.  The OpenSSL version and OpenSSL configuration determine the disabled ciphers.  If the application accepts encrypted data as input, decryption will succeed even with the wrong key.  This in turn loses the modest protection from the Modification Detection Code (MDC).  Affected functions are pgp_sym_encrypt, pgp_sym_decrypt, pgp_pub_encrypt, pgp_pub_decrypt, pgp_sym_encrypt_bytea, pgp_sym_decrypt_bytea, pgp_pub_encrypt_bytea, and pgp_pub_decrypt_bytea.  Versions before PostgreSQL 18.6, 17.11, 16.15, 15.19, and 14.24 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-14663
- https://www.postgresql.org/support/security/CVE-2026-14663/
