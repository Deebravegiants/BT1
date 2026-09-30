# [C] Issue Summary: Cryptographic Message Services (CMS) processing fails to perform sufficient input...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1135
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1135
Type: osv

## Affected
- Julia: `AppBundler` — affected >=1.0.0 <1.0.1
- Julia: `OpenSSL_jll` — affected >=3.0.8+0 <3.5.7+0
- Julia: `Openresty_jll` — affected >=1.27.1+0

## Details
Issue Summary: Cryptographic Message Services (CMS) processing fails to perform
sufficient input validation on the cipher and tag length fields of
AuthEnvelopedData containers, leading to various potential compromises.

Impact Summary: Attackers making use of these vulnerabilities may achieve
key-equivalent functionality for a given CMS recipient and/or bypass integrity
validation for a given message.

In one use case, an attacker may send a CMS message containing
AuthEnvelopedData with the cipher specified as a non-AEAD cipher.  OpenSSL
erroneously allows this selection, and attempts to decrypt and validate the
message.

An on-path attacker who captures one legitimate AES-GCM AuthEnvelopedData
addressed to the victim can re-emit it with the recipientInfos set left
byte-for-byte intact, so the victim's private key still unwraps the genuine CEK
(the content-encryption key), but with the inner OID rewritten to AES-256-OFB
(Output Feedback Mode, an unauthenticated keystream mode) and with an
attacker-chosen IV and ciphertext. The victim initializes AES-256-OFB under the
real CEK, never consults the MAC field, and `CMS_decrypt()` returns success.

If the application under attack responds to the attacker with any indicator
showing success or failure of the decryption effort, it is possible for the
attacker to use this as an oracle to obtain key equivalent functionality for the
CEK used for the chosen recipient of the message.

In another use case, an attacker can reduce the tag length of the chosen AEAD
cipher for a given AuthEnvelopedData container to be a single byte long,
allowing an attacker to brute force CMS decryption, producing an integrity
bypass for applications that trust `CMS_decrypt()` to reject modified content.

The FIPS modules are not affected by this issue.

## References
- https://github.com/advisories/GHSA-f9v2-4w9p-2cwc
- https://github.com/openssl/openssl/commit/03c1f4d45fb963aee7d5833390c507cd290182bc
- https://github.com/openssl/openssl/commit/439ed7d2c0962ce964482727264668bf277c333f
- https://github.com/openssl/openssl/commit/7947e6a81eb8776802f159fb6762cb7fcf7e34c7
- https://github.com/openssl/openssl/commit/9fd97f8cfdc2c0be214998de3b2b55c8edf6c7ac
- https://github.com/openssl/openssl/commit/d2ca86bcd43e4f17d899f347101766b6107676e0
- https://github.com/openssl/security/commit/03c1f4d45fb963aee7d5833390c507cd290182bc
- https://github.com/openssl/security/commit/439ed7d2c0962ce964482727264668bf277c333f
- https://github.com/openssl/security/commit/7947e6a81eb8776802f159fb6762cb7fcf7e34c7
- https://github.com/openssl/security/commit/9fd97f8cfdc2c0be214998de3b2b55c8edf6c7ac
- https://github.com/openssl/security/commit/d2ca86bcd43e4f17d899f347101766b6107676e0
- https://nvd.nist.gov/vuln/detail/CVE-2026-34182
- https://openssl-library.org/news/secadv/20260609.txt
