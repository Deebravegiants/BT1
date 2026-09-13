# [M] libafl has unsound usages of `core::slice::from_raw_parts_mut` 

## Summary
Severity: Medium
Advisory: GHSA-f7qj-v3vp-4856
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-12-23
Source: https://github.com/advisories/GHSA-f7qj-v3vp-4856
Type: github-advisory

## Affected
- crates.io: `libafl` — affected >=0 <0.11.2

## Details
The library breaks the safety assumptions when using unsafe API `slice::from_raw_parts_mut`. The pointer passed to `from_raw_parts_mut` is misaligned by casting `u8` to `u16` raw pointer directly, which is unsound. The bug is patched by using `align_offset`, which could make sure the memory address is aligned to 2 bytes for `u16`.  

This was patched in 0.11.2 in the [commit](https://github.com/AFLplusplus/LibAFL/pull/1530/commits/5a60cb31ef587d71d09d534bba39bd3973c4b35d).

## References
- https://github.com/AFLplusplus/LibAFL/issues/1526
- https://github.com/AFLplusplus/LibAFL/pull/1530
- https://github.com/AFLplusplus/LibAFL/pull/1530/commits/5a60cb31ef587d71d09d534bba39bd3973c4b35d
- https://github.com/AFLplusplus/LibAFL/commit/f70a16a09a8096d3c50159dd8a912a75c2af157c
- https://github.com/AFLplusplus/LibAFL
- https://rustsec.org/advisories/RUSTSEC-2024-0424.html
