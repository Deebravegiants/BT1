# [M] PHP JWT Framework: Chacha20Poly1305 key-encryption algorithm discards the Poly1305 authentication tag, performing no authentication on decryption

## Summary
Severity: Medium
Advisory: GHSA-6vvh-pxr4-25r7
CWE: CWE-347, CWE-353
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:A/AC:H/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-6vvh-pxr4-25r7
Type: github-advisory

## Affected
- Packagist: `web-token/jwt-experimental` — affected >=0
- Packagist: `web-token/jwt-library` — affected >=0 <3.4.10
- Packagist: `web-token/jwt-library` — affected >=4.0.0 <4.0.7
- Packagist: `web-token/jwt-library` — affected >=4.1.0 <4.1.7

## Details
### Impact

The experimental `Chacha20Poly1305` key-encryption algorithm generates the 16-byte Poly1305 authentication tag during `encryptKey()` but **discards it**: the tag is never written to the header and therefore never reaches the wire. On the receiving side, `decryptKey()` calls `openssl_decrypt('chacha20-poly1305', ...)` **without the tag argument**, which makes OpenSSL skip authentication entirely.

As a result the AEAD construction is silently degraded to unauthenticated ChaCha20: a tampered encrypted CEK is accepted, and because ChaCha20 is a stream cipher, a single-byte change in the ciphertext propagates as a single-byte change in the recovered CEK with no integrity check (CWE-353 / CWE-347). An attacker on the token path can manipulate the wrapped key without detection.

### Affected configurations

Applications that register `Jose\Experimental\KeyEncryption\Chacha20Poly1305` (package `web-token/jwt-experimental`) as a JWE `alg`.

### Patches

`encryptKey()` now publishes the Poly1305 tag as the base64url `tag` header parameter (and asserts it is 16 bytes). `decryptKey()` requires the `tag` header, validates its length, and passes it to `openssl_decrypt()` so the tag is actually verified, in line with RFC 7539 / RFC 8439. Tampering now results in a decryption failure.

> Note: this changes the wire format of tokens produced with this experimental algorithm (a `tag` header is now emitted and required).

### Workarounds

Do not use the experimental `Chacha20Poly1305` key-encryption algorithm for untrusted input until upgraded.

### References

- RFC 7539 / RFC 8439 (ChaCha20-Poly1305 AEAD)
- CWE-353: Missing Support for Integrity Check

## Résolution

Un correctif a été préparé sur une branche dédiée basée sur `3.4.x`, avec des tests anti-régression dédiés (fork privé temporaire de cette advisory, PR #1).

**ChaCha20-Poly1305** — le tag d'authentification Poly1305 est désormais publié dans le header au chiffrement et vérifié au déchiffrement (RFC 7539), rétablissant l'intégrité AEAD.

**Validation :** `php -l` OK, PHPUnit vert, aucune nouvelle erreur PHPStan introduite (différentiel nul vs `3.4.x`), aucun commentaire ajouté dans le code source. Après merge, cascade prévue `3.4.x → 4.0.x → 4.1.x`.

## References
- https://github.com/web-token/jwt-framework/security/advisories/GHSA-6vvh-pxr4-25r7
- https://github.com/FriendsOfPHP/security-advisories/blob/master/web-token/jwt-library/GHSA-6vvh-pxr4-25r7.yaml
- https://github.com/web-token/jwt-framework
