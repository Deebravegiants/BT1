# [H] rust-openssl: rustMdCtxRef::digest_final() writes past caller buffer with no length check

## Summary
Severity: High
Advisory: GHSA-ghm9-cr32-g9qj
CVE: CVE-2026-41681
CWE: CWE-121
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-ghm9-cr32-g9qj
Type: github-advisory

## Affected
- crates.io: `openssl` — affected >=0.10.39 <0.10.78

## Details
`EVP_DigestFinal()` always writes `EVP_MD_CTX_size(ctx)` to the `out` buffer. If `out` is smaller than that, `MdCtxRef::digest_final()` writes past its end, usually corrupting the stack. This is reachable from safe Rust.

## References
- https://github.com/rust-openssl/rust-openssl/security/advisories/GHSA-ghm9-cr32-g9qj
- https://nvd.nist.gov/vuln/detail/CVE-2026-41681
- https://github.com/rust-openssl/rust-openssl/pull/2608
- https://github.com/rust-openssl/rust-openssl/commit/826c3888b77add418b394770e2b2e3a72d9f92fe
- https://github.com/rust-openssl/rust-openssl
- https://github.com/rust-openssl/rust-openssl/releases/tag/openssl-v0.10.78
