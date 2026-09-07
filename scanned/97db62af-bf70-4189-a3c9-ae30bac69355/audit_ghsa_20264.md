# [H] Miscomputed sha2 results when using AVX2 backend

## Summary
Severity: High
Advisory: GHSA-xpww-g9jx-hp8r
Ecosystem: crates.io
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-xpww-g9jx-hp8r
Type: github-advisory

## Affected
- crates.io: `sha2` — affected >=0.9.7 <0.9.8

## Details
The v0.9.7 release of the `sha2` crate introduced a new AVX2-accelerated
backend which was automatically enabled for all x86/x86_64 CPUs where AVX2
support was autodetected at runtime.

This backend was buggy and would miscompute results for long messages
(i.e. messages spanning multiple SHA blocks).

The crate has since been yanked, but any users who upgraded to v0.9.7 should
immediately upgrade to v0.9.8 and recompute any hashes which were previously
computed by v0.9.7.

## References
- https://github.com/RustCrypto/hashes/pull/314
- https://github.com/RustCrypto/hashes
- https://rustsec.org/advisories/RUSTSEC-2021-0100.html
