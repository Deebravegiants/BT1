# [M] `SegQueue` creates zero value of any type

## Summary
Severity: Medium
Advisory: GHSA-6888-wf7j-34jq
Aliases: RUSTSEC-2022-0021
Ecosystem: crates.io
Published: 2022-06-16
Source: https://osv.dev/vulnerability/GHSA-6888-wf7j-34jq
Type: osv

## Affected
- crates.io: `crossbeam-queue` — affected >=0 <0.2.3

## Details
Affected versions of this crate called `mem::zeroed()` to create values of a user-supplied type `T`.
This is unsound e.g. if `T` is a reference type (which must be non-null).
 
The flaw was corrected by avoiding the use of `mem::zeroed()`, using `MaybeUninit` instead.

## References
- https://github.com/crossbeam-rs/crossbeam/pull/458
- https://github.com/crossbeam-rs/crossbeam
- https://rustsec.org/advisories/RUSTSEC-2022-0021.html
