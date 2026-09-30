# [M] Some AES functions may panic when overflow checking is enabled in ring

## Summary
Severity: Medium
Advisory: GHSA-4p46-pwfr-66x6
CVE: CVE-2025-4432
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-03-07
Source: https://github.com/advisories/GHSA-4p46-pwfr-66x6
Type: github-advisory

## Affected
- crates.io: `ring` — affected >=0 <0.17.12

## Details
`ring::aead::quic::HeaderProtectionKey::new_mask()` may panic when overflow checking is enabled. In the QUIC protocol, an attacker can induce this panic by sending a specially-crafted packet. Even unintentionally it is likely to occur in 1 out of every 2**32 packets sent and/or received.

On 64-bit targets operations using `ring::aead::{AES_128_GCM, AES_256_GCM}` may panic when overflow checking is enabled, when encrypting/decrypting approximately 68,719,476,700 bytes (about 64 gigabytes) of data in a single chunk. Protocols like TLS and SSH are not affected by this because those protocols break large amounts of data into small chunks. Similarly, most applications will not attempt to encrypt/decrypt 64GB of data in one chunk.

Overflow checking is not enabled in release mode by default, but `RUSTFLAGS="-C overflow-checks"` or `overflow-checks = true` in the Cargo.toml profile can override this. Overflow checking is usually enabled by default in debug mode.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-4432
- https://github.com/briansmith/ring/pull/2447
- https://github.com/briansmith/ring/commit/ec2d3cf1d91f148c84e4806b4f0b3c98f6df3b38
- https://access.redhat.com/security/cve/CVE-2025-4432
- https://bugzilla.redhat.com/show_bug.cgi?id=2350655
- https://github.com/briansmith/ring
- https://github.com/briansmith/ring/blob/main/RELEASES.md#version-01712-2025-03-05
- https://rustsec.org/advisories/RUSTSEC-2025-0009.html
