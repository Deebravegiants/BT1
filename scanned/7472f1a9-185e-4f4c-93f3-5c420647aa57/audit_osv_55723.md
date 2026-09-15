# [M] zerovec-derive incorrectly uses `#[repr(packed)]`

## Summary
Severity: Medium
Advisory: GHSA-74r5-g7vc-j2v2
Aliases: RUSTSEC-2024-0346
Ecosystem: crates.io
Published: 2024-07-08
Source: https://osv.dev/vulnerability/GHSA-74r5-g7vc-j2v2
Type: osv

## Affected
- crates.io: `zerovec-derive` — affected >=0.10.0 <0.10.3
- crates.io: `zerovec-derive` — affected >=0 <0.9.7

## Details
The affected versions make unsafe memory accesses under the assumption that `#[repr(packed)]` has a guaranteed field order. 

The Rust specification does not guarantee this, and https://github.com/rust-lang/rust/pull/125360 (1.80.0-beta) starts 
reordering fields of `#[repr(packed)]` structs, leading to illegal memory accesses.

The patched versions `0.9.7` and `0.10.3` use `#[repr(C, packed)]`, which guarantees field order.

## References
- https://github.com/unicode-org/icu4x/issues/5196#issuecomment-2214711069
- https://github.com/rustsec/advisory-db/pull/2007
- https://rustsec.org/advisories/RUSTSEC-2024-0346.html
