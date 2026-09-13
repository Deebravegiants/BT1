# [M] rust-openssl: Potential out-of-bounds write in `CipherCtxRef::cipher_update_inplace` for AES-KW-PAD ciphers

## Summary
Severity: Medium
Advisory: GHSA-phqj-4mhp-q6mq
CVE: CVE-2026-45784
CWE: CWE-131, CWE-787
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-phqj-4mhp-q6mq
Type: github-advisory

## Affected
- crates.io: `openssl` — affected >=0.10.50 <0.10.80

## Details
`CipherCtxRef::cipher_update_inplace` incorrectly sized output buffers when used with AES key-wrap-with-padding ciphers (EVP_aes_{128,192,256}_wrap_pad). For a non-multiple-of-8 input, OpenSSL writes up to 7 bytes past the end of the caller's buffer or Vec, producing attacker-controllable heap corruption when the plaintext length is attacker-influenced.

This only impacts users using AES key-wrap-with-padding ciphers.

This method was missed in the fix for GHSA-xv59-967r-8726

## References
- https://github.com/rust-openssl/rust-openssl/security/advisories/GHSA-phqj-4mhp-q6mq
- https://github.com/rust-openssl/rust-openssl
