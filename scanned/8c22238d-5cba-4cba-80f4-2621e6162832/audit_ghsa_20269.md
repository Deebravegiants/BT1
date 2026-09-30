# [H] `DecimalArray` does not perform bound checks on accessing values and offsets

## Summary
Severity: High
Advisory: GHSA-h588-76vg-prgj
Ecosystem: crates.io
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-h588-76vg-prgj
Type: github-advisory

## Affected
- crates.io: `arrow` — affected >=0 <6.4.0

## Details
`DecimalArray` performs insufficient bounds checks, which allows out-of-bounds reads in safe code if the lenght of the backing buffer is not a multiple of 16.

## References
- https://github.com/apache/arrow-rs/issues/775
- https://github.com/apache/arrow-rs
- https://rustsec.org/advisories/RUSTSEC-2021-0117.html
