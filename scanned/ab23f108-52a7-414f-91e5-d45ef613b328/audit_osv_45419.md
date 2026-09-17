# [M] Issue summary: The implementations of AES-SIV (RFC 5297) and AES-GCM-SIV (RFC 8452) mishandle the...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1144
Ecosystem: Julia
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1144
Type: osv

## Affected
- Julia: `AppBundler` — affected >=1.0.0 <1.0.1
- Julia: `OpenSSL_jll` — affected >=3.0.8+0 <3.5.7+0
- Julia: `Openresty_jll` — affected >=1.27.1+0

## Details
Issue summary: The implementations of AES-SIV (RFC 5297) and AES-GCM-SIV
(RFC 8452) mishandle the authentication of AAD (Additional Authenticated
Data) with an empty ciphertext allowing a forgery of such messages.

Impact summary: An attacker can forge empty messages with arbitrary AAD
to the victim's application using these ciphers.

AES-SIV (RFC 5297) and AES-GCM-SIV (RFC 8452) are nonce-misuse-resistant AEAD
modes: they accept a key, nonce, optional AAD (bytes that are authenticated
but not encrypted), and plaintext, and produces ciphertext plus a 16-byte
tag. On decrypt, `EVP_DecryptFinal_ex()` is documented to return success only
if the tag is verified succesfully.

In OpenSSL's provider implementation of these ciphers, the expected tag is
computed only when decryption function is invoked with non-empty data.
If the caller supplies AAD and then calls `EVP_DecryptFinal_ex()` without
invocation of the ciphertext update, which can happen when the received
ciphertext length is zero, the tag is never recalculated and still holds its
all-zeros value.

When AES-GCM-SIV is used, an attacker who sends arbitrary AAD, empty
ciphertext, and all-zeros tag passes authentication under any key they do not
know, single-shot. When AES-SIV is used, for mounting the attack it's
necessary for the application to reuse the decryption context without
resetting the key.

AES-SIV is implemented since OpenSSL 3.0. AES-GCM-SIV is implemented since
OpenSSL 3.2.

No protocols implemented in OpenSSL itself (TLS/CMS/PKCS7/HPKE/QUIC) support
either AES-GCM-SIV or AES-SIV. To mount an attack, the applications must
implement their own protocol and use the EVP interface. Also they must skip the
ciphertext update when a message with an empty ciphertext arrives.

The FIPS modules in 4.0, 3.6, 3.5, 3.4, and 3.0 are not affected by this
issue, as these algorithms are not FIPS approved and the affected code is
outside the OpenSSL FIPS module boundary.

## References
- https://github.com/advisories/GHSA-7phf-qpm5-q6p3
- https://github.com/openssl/openssl/commit/25b32cd9d41d2bc01b6abc425bb4baf2c2236fdc
- https://github.com/openssl/openssl/commit/71e2a5d263518cf5866043bd60ee4994d59e53a3
- https://github.com/openssl/openssl/commit/7fe3f33a3b3a4c487aa4dcdbc87057f66ffd2b85
- https://github.com/openssl/openssl/commit/daca0f48e4a69a2892a62262bad59e62a8a76598
- https://github.com/openssl/openssl/commit/eec5e9bf0d867333b8495e456f5235d225798a68
- https://github.com/openssl/security/commit/25b32cd9d41d2bc01b6abc425bb4baf2c2236fdc
- https://github.com/openssl/security/commit/71e2a5d263518cf5866043bd60ee4994d59e53a3
- https://github.com/openssl/security/commit/7fe3f33a3b3a4c487aa4dcdbc87057f66ffd2b85
- https://github.com/openssl/security/commit/daca0f48e4a69a2892a62262bad59e62a8a76598
- https://github.com/openssl/security/commit/eec5e9bf0d867333b8495e456f5235d225798a68
- https://nvd.nist.gov/vuln/detail/CVE-2026-45446
- https://openssl-library.org/news/secadv/20260609.txt
