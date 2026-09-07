# [M] Maligned causes incorrect deallocation

## Summary
Severity: Medium
Advisory: GHSA-wm8x-php5-hvq6
Ecosystem: crates.io
Published: 2023-03-07
Source: https://github.com/advisories/GHSA-wm8x-php5-hvq6
Type: github-advisory

## Affected
- crates.io: `maligned` — affected >=0

## Details
`maligned::align_first` manually allocates with an alignment larger than T, and then uses `Vec::from_raw_parts` on that allocation to get a `Vec<T>`.

[`GlobalAlloc::dealloc`](https://doc.rust-lang.org/std/alloc/trait.GlobalAlloc.html#tymethod.dealloc) requires that the `layout` argument must be the same layout that was used to allocate that block of memory.

When deallocating, `Box` and `Vec` may not respect the specified alignment and can cause undefined behavior.

## References
- https://github.com/tylerhawkes/maligned/issues/5
- https://doc.rust-lang.org/std/alloc/trait.GlobalAlloc.html#tymethod.dealloc
- https://github.com/tylerhawkes/maligned
- https://rustsec.org/advisories/RUSTSEC-2023-0017.html
