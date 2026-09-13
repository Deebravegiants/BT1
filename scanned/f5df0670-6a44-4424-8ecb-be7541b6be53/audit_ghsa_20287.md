# [H] `Read` on uninitialized memory may cause UB (fn preamble_skipcount())

## Summary
Severity: High
Advisory: GHSA-r67p-m7g9-gxw6
Ecosystem: crates.io
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-r67p-m7g9-gxw6
Type: github-advisory

## Affected
- crates.io: `csv-sniffer` — affected >=0 <0.2.0

## Details
Affected versions of this crate passes an uninitialized buffer to a user-provided `Read` implementation (within `fn preamble_skipcount()`).

Arbitrary `Read` implementations can read from the uninitialized buffer (memory exposure) and also can return incorrect number of bytes written to the buffer.
Reading from uninitialized memory produces undefined values that can quickly invoke undefined behavior.

## References
- https://github.com/jblondin/csv-sniffer/issues/1
- https://github.com/jblondin/csv-sniffer/pull/2
- https://rustsec.org/advisories/RUSTSEC-2021-0088.html
