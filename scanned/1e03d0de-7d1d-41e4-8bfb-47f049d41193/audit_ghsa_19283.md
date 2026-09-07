# [M] fast_id_map has a soundness issue and is unmaintained

## Summary
Severity: Medium
Advisory: GHSA-4h96-mv53-2c86
CWE: CWE-20
Ecosystem: crates.io
Published: 2025-05-08
Source: https://github.com/advisories/GHSA-4h96-mv53-2c86
Type: github-advisory

## Affected
- crates.io: `fast_id_map` — affected >=0

## Details
`FastMap::get()` lacks sufficient checks to its parameter index and is used to unsafely get a `Vec` element.

`fast_id_map` is unmaintained.

## References
- https://github.com/Bruce0203/fast_map
- https://rustsec.org/advisories/RUSTSEC-2025-0034.html
