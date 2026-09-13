# [M] smallvec creates uninitialized value of any type

## Summary
Severity: Medium
Advisory: GHSA-66p5-j55p-32r9
CWE: CWE-457
Ecosystem: crates.io
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-66p5-j55p-32r9
Type: github-advisory

## Affected
- crates.io: `smallvec` — affected >=0 <0.6.13

## Details
Affected versions of this crate called `mem::uninitialized()` to create values of a user-supplied type `T`.
This is unsound e.g. if `T` is a reference type (which must be non-null and thus may not remain uninitialized).
 
The flaw was corrected by avoiding the use of `mem::uninitialized()`, using `MaybeUninit` instead.

## References
- https://github.com/servo/rust-smallvec/issues/126
- https://github.com/servo/rust-smallvec/pull/162
- https://github.com/servo/rust-smallvec
- https://rustsec.org/advisories/RUSTSEC-2018-0018.html
