# [M] `out_reference::Out::from_raw` should be `unsafe`

## Summary
Severity: Medium
Advisory: GHSA-p7mj-xvxg-grff
Ecosystem: crates.io
Published: 2023-03-13
Source: https://github.com/advisories/GHSA-p7mj-xvxg-grff
Type: github-advisory

## Affected
- crates.io: `out-reference` — affected >=0.1.0 <0.2.0

## Details
`Out::from_raw` in affected versions allows writing a value to invalid memory address without requiring `unsafe`.

The soundness issue has been addressed by making `Out::from_raw` an unsafe function.

## References
- https://github.com/RustyYato/out-ref/issues/1
- https://rustsec.org/advisories/RUSTSEC-2021-0152.html
