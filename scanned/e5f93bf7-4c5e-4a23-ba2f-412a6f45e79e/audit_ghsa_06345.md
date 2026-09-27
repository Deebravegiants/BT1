# [H] cryptography: PKCS#7 EnvelopedData decryption exposes a Bleichenbacher oracle through distinguishable errors and timing

## Summary
Severity: High
Advisory: GHSA-g6cj-pr64-35w5
CVE: CVE-2026-69247
CWE: CWE-208, CWE-209
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-g6cj-pr64-35w5
Type: github-advisory

## Affected
- PyPI: `cryptography` — affected >=44.0.0 <50.0.0

## Details
### Summary

`pkcs7_decrypt_der`, `pkcs7_decrypt_pem`, and `pkcs7_decrypt_smime` reported the
outcome of decrypting a `RecipientInfo`'s `encryptedKey` in several
distinguishable ways, one of which disclosed the exact length recovered from the
RSA operation. The same distinction was also observable by timing. An
application that decrypts attacker-supplied `EnvelopedData` and reflects the
outcome gives the attacker a Bleichenbacher oracle against the
content-encryption key.

Introduced in 44.0.0. Fixed in 50.0.0.

### Details

Decryption ran as: RSA PKCS#1 v1.5 decrypt of `encryptedKey` → build an AES
cipher from the result → AES-CBC decrypt and PKCS#7 unpad. Each stage failed
differently, with no RFC 3218 mitigation:

1. invalid RSA padding → `Decryption failed`
2. valid padding, bad key length → `Invalid key size (N) for AES.`, disclosing `N`
3. correct length, wrong key → `Invalid padding bytes.`
4. the real key → plaintext

Case 1 is reachable only where the linked library lacks implicit rejection:
OpenSSL 3.0 and 3.1, LibreSSL, and BoringSSL. On OpenSSL 3.2+, used in our wheels,
invalid padding instead returns a synthetic plaintext of
pseudorandom length, so the error channel does not distinguish conforming
ciphertexts.

Exploitation requires a service that auto-decrypts untrusted `EnvelopedData`
matching the victim certificate and answers adaptively at high volume, such as
an S/MIME gateway or mail filter.

### Fix

Per RFC 3218, the content-encryption algorithm is now resolved before the
private key is used, so the expected key length is known in advance. If the RSA
decryption fails or recovers a key of the wrong length, a random key of the
expected length is substituted and decryption continues down an identical path.
All failures now report identically and perform the same work.

### Not addressed by this fix

`EnvelopedData` does not authenticate its content. Tampering with
`encryptedContent` alone yields a CBC padding oracle that recovers plaintext at
roughly 256 queries per byte, without recovering any key, on every backend. This
is a property of PKCS#7 rather than of this implementation, cannot be fixed in
the library, and is now documented.

### Credit

Reported by @X1AOxiang.

## References
- https://github.com/pyca/cryptography/security/advisories/GHSA-g6cj-pr64-35w5
- https://github.com/pyca/cryptography/pull/15369
- https://github.com/pyca/cryptography/commit/53fccd93413a8d7f07d6d8999681f27b75cffa3f
- https://github.com/pyca/cryptography
