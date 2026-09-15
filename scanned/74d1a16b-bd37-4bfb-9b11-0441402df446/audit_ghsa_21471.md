# [M] Invalid use of `mem::uninitialized` causes `use-of-uninitialized-value`

## Summary
Severity: Medium
Advisory: GHSA-5m39-wx2q-mxg3
Ecosystem: crates.io
Published: 2022-11-08
Source: https://github.com/advisories/GHSA-5m39-wx2q-mxg3
Type: github-advisory

## Affected
- crates.io: `lzf` — affected >=0 <0.3.2

## Details
The compression and decompression function used `mem:uninitialized` to create an array of uninitialized values, to later write values into it. This later leads to reads from uninitialized memory.

The flaw was corrected in commit b633bf265e41c60dfce3be7eac4e4dd5e18d06cf by using a heap-allocated `Vec` and removing out use of `mem::uninitialized`. The fix was released in v0.3.2 and v1.0.0

Subsequently, the crate was deprecated and its use is discouraged.

## References
- https://github.com/badboy/lzf-rs/issues/9
- https://github.com/badboy/lzf-rs/commit/b633bf265e41c60dfce3be7eac4e4dd5e18d06cf
- https://github.com/badboy/lzf-rs
- https://rustsec.org/advisories/RUSTSEC-2022-0067.html
