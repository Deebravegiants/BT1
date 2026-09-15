# [H] Counter overflow in chacha20

## Summary
Severity: High
Advisory: GHSA-j2r6-2m5c-vgh5
CVE: CVE-2019-25005
CWE: CWE-190
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-j2r6-2m5c-vgh5
Type: github-advisory

## Affected
- crates.io: `chacha20` — affected >=0 <0.2.3

## Details
An issue was discovered in the chacha20 crate before 0.2.3 for Rust. A ChaCha20 counter overflow makes it easier for attackers to determine plaintext.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25005
- https://github.com/RustCrypto/stream-ciphers/pull/64
- https://github.com/RustCrypto/stream-ciphers/tree/master/chacha20
- https://rustsec.org/advisories/RUSTSEC-2019-0029.html
