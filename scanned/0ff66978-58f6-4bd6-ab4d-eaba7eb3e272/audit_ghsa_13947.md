# [M] partial_sort contains Out-of-bounds Read in release mode

## Summary
Severity: Medium
Advisory: GHSA-5x36-7567-3cw6
CWE: CWE-125
Ecosystem: crates.io
Published: 2023-02-28
Source: https://github.com/advisories/GHSA-5x36-7567-3cw6
Type: github-advisory

## Affected
- crates.io: `partial_sort` — affected >=0 <0.2.0

## Details
Affected versions of this crate were using a debug assertion to validate the `last` parameter of `partial_sort()`. This would allow invalid inputs to cause an out-of-bounds read instead of immediately panicking, when compiled without debug assertions.

All writes are bounds-checked, so the out-of-bounds memory access is read-only. This also means that the first attempted out-of-bounds write will panic, limiting the possible reads.

The accessible region is further limited by an initial bounds-checked read at `(last / 2) - 1`, i.e., it is proportional to the size of the vector.

This bug has been fixed in v0.2.0.

## References
- https://github.com/sundy-li/partial_sort/issues/7
- https://github.com/sundy-li/partial_sort
- https://rustsec.org/advisories/RUSTSEC-2023-0016.html
