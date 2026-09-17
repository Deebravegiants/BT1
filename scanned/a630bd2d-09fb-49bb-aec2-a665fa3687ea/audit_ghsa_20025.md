# [M] prettytable-rs: Force cast a &Vec<T> to &[T] may lead to undefined behavior

## Summary
Severity: Medium
Advisory: GHSA-gfgm-chr3-x6px
Ecosystem: crates.io
Published: 2022-12-30
Source: https://github.com/advisories/GHSA-gfgm-chr3-x6px
Type: github-advisory

## Affected
- crates.io: `prettytable-rs` — affected >=0 <0.10.0

## Details
In function `Table::as_ref`, a reference of vector is force cast to slice. There are multiple problems here:
1. To guarantee the size is correct, we have to first do `Vec::shrink_to_fit`. The function requires a mutable reference, so we have to force cast from immutable to mutable, which is undefined behavior (UB).
2. Even if (1) is sound, `&Vec<T>` and `&[T]` still might not have the same layout. Treating them equally may lead to undefinted behavior (UB).

## References
- https://github.com/phsym/prettytable-rs/issues/145
- https://github.com/phsym/prettytable-rs
- https://rustsec.org/advisories/RUSTSEC-2022-0074.html
