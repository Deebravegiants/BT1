# [M] rust-openssl vulnerable to heap buffer overflow when encrypting with AES key-wrap-with-padding

## Summary
Severity: Medium
Advisory: GHSA-xv59-967r-8726
CVE: CVE-2026-44662
CWE: CWE-122
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-xv59-967r-8726
Type: github-advisory

## Affected
- crates.io: `openssl` — affected >=0.10.0 <0.10.79

## Details
`CipherCtxRef::cipher_update`, `CipherCtxRef::cipher_update_vec`, and `symm::Crypter::update` incorrectly sized output buffers when used with AES key-wrap-with-padding ciphers (`EVP_aes_{128,192,256}_wrap_pad`). For a non-multiple-of-8 input, OpenSSL writes up to 7 bytes past the end of the caller's buffer or Vec, producing attacker-controllable heap corruption when the plaintext length is attacker-influenced.

This only impacts users using AES key-wrap-with-padding ciphers.

## References
- https://github.com/rust-openssl/rust-openssl/security/advisories/GHSA-xv59-967r-8726
- https://nvd.nist.gov/vuln/detail/CVE-2026-44662
- https://github.com/rust-openssl/rust-openssl
