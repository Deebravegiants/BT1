# [M] Ascii (crate) allows out-of-bounds array indexing in safe code

## Summary
Severity: Medium
Advisory: GHSA-mrrw-grhq-86gf
CWE: CWE-119
Ecosystem: crates.io
Published: 2023-02-28
Source: https://github.com/advisories/GHSA-mrrw-grhq-86gf
Type: github-advisory

## Affected
- crates.io: `ascii` — affected >=0.7.0 <0.9.3

## Details
Affected version of this crate had implementation of `From<&mut AsciiStr>` for `&mut [u8]` and `&mut str`. This can result in out-of-bounds array indexing in safe code.

The flaw was corrected in commit [8a6c779](https://github.com/tomprogrammer/rust-ascii/pull/63/commits/8a6c7798c202766bd57d70fb8d12739dd68fb9dc) by removing those impls.

## References
- https://github.com/tomprogrammer/rust-ascii/issues/64
- https://github.com/tomprogrammer/rust-ascii/pull/63/commits/8a6c7798c202766bd57d70fb8d12739dd68fb9dc
- https://github.com/tomprogrammer/rust-ascii
- https://rustsec.org/advisories/RUSTSEC-2023-0015.html
