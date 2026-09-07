# [C] wee_alloc is Unmaintained

## Summary
Severity: Critical
Advisory: GHSA-rc23-xxgq-x27g
Ecosystem: crates.io
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-rc23-xxgq-x27g
Type: github-advisory

## Affected
- crates.io: `wee_alloc` — affected >=0

## Details
Two of the maintainers have indicated that the crate may not be maintained.

The crate has open issues including memory leaks and may not be suitable for production use.

It may be best to switch to the default Rust standard allocator on wasm32 targets.

Last release seems to have been three years ago.

## References
- https://github.com/rustwasm/wee_alloc/issues/107
- https://github.com/rustwasm/wee_alloc
- https://rustsec.org/advisories/RUSTSEC-2022-0054.html
