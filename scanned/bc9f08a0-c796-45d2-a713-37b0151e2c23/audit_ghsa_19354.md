# [M] tanton_engine has unsound public API

## Summary
Severity: Medium
Advisory: GHSA-m2xr-2vj4-wh94
CWE: CWE-119
Ecosystem: crates.io
Published: 2025-05-06
Source: https://github.com/advisories/GHSA-m2xr-2vj4-wh94
Type: github-advisory

## Affected
- crates.io: `tanton_engine` — affected >=0

## Details
The following functions in the `tanton_engine` crate are unsound due to lack of sufficient boundary
checks in public API:

- `Stack::offset()`
- `ThreadStack::get()`
- `RootMoveList::insert_score_depth()`
- `RootMoveList::insert_score()`

The tanton_engine crate is no longer maintained, so there are no plans to fix this issue.

## References
- https://rustsec.org/advisories/RUSTSEC-2025-0031.html
