# [M] vec-const attempts to construct a Vec from a pointer to a const slice

## Summary
Severity: Medium
Advisory: GHSA-jmwx-r3gq-qq3p
Ecosystem: crates.io
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-jmwx-r3gq-qq3p
Type: github-advisory

## Affected
- crates.io: `vec-const` — affected >=0 <2.0.0

## Details
Affected versions of this crate claimed to construct a const `Vec` with nonzero length and capacity, but that cannot be done because such a `Vec` requires a pointer from an allocator.

The implementation was later changed to just construct a `std::borrow::Cow`.

## References
- https://github.com/Eolu/vec-const/issues/1#issuecomment-898908241
- https://github.com/Eolu/vec-const
- https://rustsec.org/advisories/RUSTSEC-2021-0082.html
