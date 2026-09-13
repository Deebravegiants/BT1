# [C] AEAD Forgeries with Empty Ciphertext When Using EVP_Cipher()

## Summary
Severity: Critical
Advisory: CVE-2026-75803
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-75803
Type: osv

## Details
Issue summary: ChaCha20-Poly1305 and AES-OCB decryption with an empty
ciphertext can report success without verifying the supplied authentication
tag when the operation is finalized by calling the EVP_Cipher() function.

Impact summary: Applications calling EVP_Cipher() on an empty ciphertext and
expecting the call to check the AEAD tag may accept forged messages.

CWE: CWE-354 (Improper Validation of Integrity Check Value)

Description: The EVP_Cipher() API call for AEAD ciphers behaves like a one
shot encryption and decryption call. It also verifies the AEAD tag after the
decryption operation. However for AES-OCB and ChaCha20-Poly1305 ciphers
it skipped the AEAD tag verification when an empty ciphertext was passed to
the function. The callers of this function might believe that a successful
return indicates a valid AEAD tag for these ciphers, even when that has not
truly been validated in this case.

FIPS impact: no
The FIPS modules in 4.0, 3.6, 3.5, 3.4, and 3.0 are not affected by this CVE
as the affected algorithms are not FIPS approved and thus not implemented
in the FIPS module.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75803.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75803
- https://openssl-library.org/news/secadv/20260825.txt
- https://github.com/openssl/openssl/commit/119ab9555dc62275bbd71f6f49529b1a44feba42
- https://github.com/openssl/openssl/commit/3621257986e27e540bf96a11570929a6e5a9e05b
- https://github.com/openssl/openssl/commit/6c7aa6f8f6449b7fe0137ee8be65fcd239bd7d6a
- https://github.com/openssl/openssl/commit/bdeb0cd994d915342787f117ee75044f0dc36f34
- https://github.com/openssl/openssl/commit/bf95f5f772e9362f87b25cfa2f8cb15d984865b9
