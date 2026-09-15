# [M] impl `FromMdbValue` for bool is unsound

## Summary
Severity: Medium
Advisory: GHSA-f9g6-fp84-fv92
Ecosystem: crates.io
Published: 2023-07-19
Source: https://github.com/advisories/GHSA-f9g6-fp84-fv92
Type: github-advisory

## Affected
- crates.io: `lmdb-rs` — affected >=0

## Details
The implementation of `FromMdbValue` has several unsoundness issues. First of all, it allows to reinterpret arbitrary bytes as a bool and could make undefined behavior happen with safe function. Secondly, it allows transmuting pointer without taking memory layout into consideration. The details of reproducing the bug are available [here](https://github.com/vhbit/lmdb-rs/issues/67).

## References
- https://github.com/vhbit/lmdb-rs/issues/67
- https://github.com/vhbit/lmdb-rs
- https://rustsec.org/advisories/RUSTSEC-2023-0047.html
