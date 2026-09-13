# [H] rust-openssl: Deriver::derive and PkeyCtxRef::derive can overflow short buffers on OpenSSL 1.1.1

## Summary
Severity: High
Advisory: GHSA-pqf5-4pqq-29f5
CVE: CVE-2026-41676
CWE: CWE-131, CWE-787
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-pqf5-4pqq-29f5
Type: github-advisory

## Affected
- crates.io: `openssl` — affected >=0.9.27 <0.10.78

## Details
`Deriver::derive` (and `PkeyCtxRef::derive`) sets `len = buf.len()` and passes it as the in/out length to `EVP_PKEY_derive`, relying on OpenSSL to honor it. On OpenSSL 1.1.x, X25519, X448, DH and HKDF-extract  ignore the incoming `*keylen`, unconditionally writing the full shared secret (32/56/prime-size bytes). A caller passing a short slice gets a heap/stack overflow from safe code. OpenSSL 3.x providers do check, so this only impacts older OpenSSL.

## References
- https://github.com/rust-openssl/rust-openssl/security/advisories/GHSA-pqf5-4pqq-29f5
- https://nvd.nist.gov/vuln/detail/CVE-2026-41676
- https://github.com/rust-openssl/rust-openssl/pull/2606
- https://github.com/rust-openssl/rust-openssl/commit/09b425e5f59a2466d806e71a83a9a449c914c596
- https://github.com/rust-openssl/rust-openssl
- https://github.com/rust-openssl/rust-openssl/releases/tag/openssl-v0.10.78
