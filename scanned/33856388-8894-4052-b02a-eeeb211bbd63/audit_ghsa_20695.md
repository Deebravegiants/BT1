# [M] `temporary` makes use of uninitialized memory

## Summary
Severity: Medium
Advisory: GHSA-2jq9-6xx7-3h29
Ecosystem: crates.io
Published: 2022-08-11
Source: https://github.com/advisories/GHSA-2jq9-6xx7-3h29
Type: github-advisory

## Affected
- crates.io: `temporary` — affected >=0.3.0 <0.6.4

## Details
Uninitialized memory is used as a RNG seed in temporary. This has been resolved in the 0.6.4 release. The crate is not intended to be used outside of a testing environment. For a general purpose crate to create temporary directories, [`tempfile`](https://crates.io/crates/tempfile) is an alternative for this crate.

## References
- https://github.com/stainless-steel/temporary/issues/2
- https://github.com/stainless-steel/temporary
- https://rustsec.org/advisories/RUSTSEC-2018-0022.html
