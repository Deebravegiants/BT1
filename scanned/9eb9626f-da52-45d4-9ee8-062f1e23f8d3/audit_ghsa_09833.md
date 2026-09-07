# [H] rust-openssl: Unchecked callback length in PSK/cookie trampolines leaks adjacent memory to peer

## Summary
Severity: High
Advisory: GHSA-hppc-g8h3-xhp3
CVE: CVE-2026-41898
CWE: CWE-126, CWE-130
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-hppc-g8h3-xhp3
Type: github-advisory

## Affected
- crates.io: `openssl` — affected >=0.9.24 <0.10.78

## Details
The FFI trampolines behind `SslContextBuilder::set_psk_client_callback`, `set_psk_server_callback`, `set_cookie_generate_cb`,  and `set_stateless_cookie_generate_cb` forwarded the user closure's returned usize directly to OpenSSL without checking it against the `&mut [u8]` that was handed to the closure. This can lead to buffer overflows and other unintended consequences.

## References
- https://github.com/rust-openssl/rust-openssl/security/advisories/GHSA-hppc-g8h3-xhp3
- https://nvd.nist.gov/vuln/detail/CVE-2026-41898
- https://github.com/rust-openssl/rust-openssl/pull/2607
- https://github.com/rust-openssl/rust-openssl/commit/1d109020d98fff2fb2e45c39a373af3dff99b24c
- https://github.com/rust-openssl/rust-openssl
- https://github.com/rust-openssl/rust-openssl/releases/tag/openssl-v0.10.78
