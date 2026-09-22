# [H] AES-OCB IV Ignored on EVP_Cipher() Path

## Summary
Severity: High
Advisory: CVE-2026-45445
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-45445
Type: osv

## Details
Issue summary: When an application drives an AES-OCB context through the
public EVP_Cipher() one-shot interface, the application-supplied
initialisation vector (IV) is silently discarded.

Impact summary: Every message encrypted under the same key uses the
same effective nonce regardless of the IV supplied by the caller,
resulting in (key, nonce) reuse and loss of confidentiality.  If the
same code path is used to compute the authentication tag, the tag
depends only on the (key, IV) pair and not on the plaintext or
ciphertext, allowing universal forgery of arbitrary ciphertext from a
single captured message.

OpenSSL provides two ways to drive a cipher: the documented streaming
interface (EVP_CipherUpdate / EVP_CipherFinal_ex) and a lower-level
one-shot, EVP_Cipher(), whose documentation explicitly recommends
against use by applications in favour of EVP_CipherUpdate() and
EVP_CipherFinal_ex().  The OCB provider's streaming handler flushes
the application-supplied IV into the OCB context before processing
data; the one-shot handler did not.  Every call to EVP_Cipher() on an
AES-OCB context therefore ran with the all-zero key-derived offset
state left by cipher initialisation, regardless of the caller's IV.

If EVP_EncryptFinal_ex() is subsequently used to obtain the
authentication tag, the deferred IV setup runs at that point and
clears the running checksum that should have been accumulated over the
plaintext.  The resulting tag is a function of (key, IV) only and
verifies against any ciphertext produced under the same (key, IV)
pair.

The OpenSSL SSL/TLS implementation is not affected: AES-OCB is not a
TLS cipher suite, and libssl does not call EVP_Cipher() in any case.
Applications that drive AES-OCB through the documented streaming AEAD
API (EVP_CipherUpdate / EVP_CipherFinal_ex) are not affected.  Only
applications that combine the AES-OCB cipher with the EVP_Cipher()
one-shot API are vulnerable.

The FIPS modules in 4.0, 3.6, 3.5, 3.4 and 3.0 are not affected by
this issue, as AES-OCB is outside the OpenSSL FIPS module boundary.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45445.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45445
- https://openssl-library.org/news/secadv/20260609.txt
- https://github.com/openssl/openssl/commit/323f0b6e7d530a4cb4336d50c88cb70f3ac2a451
- https://github.com/openssl/openssl/commit/787a6dfba81b7b09c1e05ab31396c0cd7c36b3f7
- https://github.com/openssl/openssl/commit/7ac4715234ee72d9f3c93426a2c08554b5b771af
- https://github.com/openssl/openssl/commit/843c9b94ca9c2ed248bb30127bb4f3d7af0d607c
- https://github.com/openssl/openssl/commit/983d54b5cce8d16147548ed1a37892d1720bbab6
