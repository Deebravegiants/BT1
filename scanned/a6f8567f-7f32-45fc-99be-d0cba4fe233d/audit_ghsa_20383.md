# [H] columnar: `Read` on uninitialized buffer may cause UB (ColumnarReadExt::read_typed_vec())

## Summary
Severity: High
Advisory: GHSA-cxcc-q839-2cw9
Ecosystem: crates.io
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-cxcc-q839-2cw9
Type: github-advisory

## Affected
- crates.io: `columnar` — affected >=0

## Details
Affected versions of this crate passes an uninitialized buffer to a user-provided `Read` implementation (`ColumnarReadExt::read_typed_vec()`).
Arbitrary `Read` implementations can read from the uninitialized buffer (memory exposure) and also can return incorrect number of bytes written to the buffer.
Reading from uninitialized memory produces undefined values that can quickly invoke undefined behavior.

## References
- https://github.com/frankmcsherry/columnar/issues/6
- https://github.com/frankmcsherry/columnar
- https://rustsec.org/advisories/RUSTSEC-2021-0087.html
