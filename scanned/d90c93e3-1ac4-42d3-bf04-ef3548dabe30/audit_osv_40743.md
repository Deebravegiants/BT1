# [H] wolfSSL EVP ChaCha20-Poly1305 AEAD authentication tag

## Summary
Severity: High
Advisory: CVE-2026-5479
CVSS: 7.5 (CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-5479
Type: osv

## Details
In wolfSSL's EVP layer, the ChaCha20-Poly1305 AEAD decryption path in wolfSSL_EVP_CipherFinal (and related EVP cipher finalization functions) fails to verify the authentication tag before returning plaintext to the caller. When an application uses the EVP API to perform ChaCha20-Poly1305 decryption, the implementation computes or accepts the tag but does not compare it against the expected value.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5479.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5479
- https://github.com/wolfSSL/wolfssl/pull/10102
- https://github.com/wolfSSL/wolfssl
