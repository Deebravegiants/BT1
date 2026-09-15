# [M] openssl's `MemBio::get_buf` has undefined behavior with empty buffers

## Summary
Severity: Medium
Advisory: GHSA-q445-7m23-qrmw
CWE: CWE-476
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-07-22
Source: https://github.com/advisories/GHSA-q445-7m23-qrmw
Type: github-advisory

## Affected
- crates.io: `openssl` — affected >=0 <0.10.66

## Details
Previously, `MemBio::get_buf` called `slice::from_raw_parts` with a null-pointer, which violates the functions invariants, leading to undefined behavior. In debug builds this would produce an assertion failure. This is now fixed.

## References
- https://github.com/sfackler/rust-openssl/pull/2266
- https://github.com/sfackler/rust-openssl/commit/aef36e0f3950653148d6644309ee41ccf16e02bb
- https://github.com/sfackler/rust-openssl
- https://github.com/sfackler/rust-openssl/releases/tag/openssl-v0.10.66
- https://rustsec.org/advisories/RUSTSEC-2024-0357.html
