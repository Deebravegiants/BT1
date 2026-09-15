# [H] Use after free in lru crate

## Summary
Severity: High
Advisory: GHSA-qqmc-hwqp-8g2w
Ecosystem: crates.io
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-qqmc-hwqp-8g2w
Type: github-advisory

## Affected
- crates.io: `lru` — affected >=0 <0.7.1

## Details
Lru crate has use after free vulnerability.

Lru crate has two functions for getting an iterator. Both iterators give
references to key and value. Calling specific functions, like pop(), will remove
and free the value, and but it's still possible to access the reference of value
which is already dropped causing use after free.

## References
- https://github.com/jeromefroe/lru-rs/issues/120
- https://github.com/jeromefroe/lru-rs
- https://rustsec.org/advisories/RUSTSEC-2021-0130.html
