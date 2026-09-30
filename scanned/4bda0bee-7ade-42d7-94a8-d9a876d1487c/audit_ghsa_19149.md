# [M] grcov has an out of bounds write triggered by crafted coverage data

## Summary
Severity: Medium
Advisory: GHSA-qm2p-4w45-v2vr
CWE: CWE-787
Ecosystem: crates.io
Published: 2025-02-10
Source: https://github.com/advisories/GHSA-qm2p-4w45-v2vr
Type: github-advisory

## Affected
- crates.io: `grcov` — affected >=0 <0.8.20

## Details
Function `grcov::covdir::get_coverage` uses the `unsafe` function `get_unchecked_mut` without validating that the index is in bounds.

This results in memory corruption, and could potentially allow arbitrary code execution provided that an attacker can feed the tool crafted coverage data.

## References
- https://github.com/mozilla/grcov/commit/c8219563bc91615dd4a27884a5c63f09db8d03bb
- https://bugzilla.mozilla.org/show_bug.cgi?id=1917475
- https://github.com/mozilla/grcov
- https://rustsec.org/advisories/RUSTSEC-2025-0005.html
