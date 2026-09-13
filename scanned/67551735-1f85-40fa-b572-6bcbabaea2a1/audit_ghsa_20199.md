# [H] Channel creates zero value of any type

## Summary
Severity: High
Advisory: GHSA-9g55-pg62-m8hh
Ecosystem: crates.io
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-9g55-pg62-m8hh
Type: github-advisory

## Affected
- crates.io: `crossbeam-channel` — affected >=0 <0.4.3

## Details
Affected versions of this crate called `mem::zeroed()` to create values of a user-supplied type `T`.
This is unsound e.g. if `T` is a reference type (which must be non-null).
 
The flaw was corrected by avoiding the use of `mem::zeroed()`, using `MaybeUninit` instead.

## References
- https://github.com/crossbeam-rs/crossbeam/pull/458
- https://github.com/crossbeam-rs/crossbeam
- https://rustsec.org/advisories/RUSTSEC-2022-0019.html
