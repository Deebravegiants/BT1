# [M] `ruzstd` uninit and out-of-bounds memory reads

## Summary
Severity: Medium
Advisory: GHSA-x3f4-45xf-rjm7
CWE: CWE-125
Ecosystem: crates.io
Published: 2024-12-02
Source: https://github.com/advisories/GHSA-x3f4-45xf-rjm7
Type: github-advisory

## Affected
- crates.io: `ruzstd` — affected >=0.7.0 <0.7.3

## Details
Affected versions of `ruzstd` miscalculate the length of the allocated and init section of its internal `RingBuffer`, leading to uninitialized or out-of-bounds reads in `copy_bytes_overshooting` of up to 15 bytes.

This may result in up to 15 bytes of memory contents being written into the decoded data when decompressing a crafted archive. This may occur multiple times per archive.

## References
- https://github.com/KillingSpark/zstd-rs/issues/75
- https://github.com/KillingSpark/zstd-rs/pull/76
- https://github.com/KillingSpark/zstd-rs
- https://rustsec.org/advisories/RUSTSEC-2024-0400.html
