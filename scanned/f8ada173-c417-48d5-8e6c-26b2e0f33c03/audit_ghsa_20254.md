# [M] Aliased mutable references from `tls_rand` & `TlsWyRand`

## Summary
Severity: Medium
Advisory: GHSA-p6gj-gpc8-f8xw
Ecosystem: crates.io
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-p6gj-gpc8-f8xw
Type: github-advisory

## Affected
- crates.io: `nanorand` — affected >=0.5.0 <0.6.1

## Details
`TlsWyRand`'s implementation of `Deref` unconditionally dereferences a raw pointer, and returns 
multiple mutable references to the same object, which is undefined behavior.

## References
- https://github.com/Absolucy/nanorand-rs/issues/28
- https://github.com/Absolucy/nanorand-rs
- https://rustsec.org/advisories/RUSTSEC-2021-0114.html
