# [M] ALPINE-CVE-2026-45446

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-45446
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-45446
Type: osv

## Affected
- Alpine:v3.22: `openssl` — affected >=3.0.0 <3.5.7-r0
- Alpine:v3.23: `openssl` — affected >=3.0.0 <3.5.7-r0
- Alpine:v3.24: `openssl` — affected >=3.0.0 <3.5.7-r0

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
- https://security.alpinelinux.org/vuln/CVE-2026-45446
