# [M] Inventory fails to prohibit standard library access prior to initialization of Rust standard library runtime

## Summary
Severity: Medium
Advisory: GHSA-ghc8-5cgm-5rpf
Ecosystem: crates.io
Published: 2023-09-11
Source: https://github.com/advisories/GHSA-ghc8-5cgm-5rpf
Type: github-advisory

## Affected
- crates.io: `inventory` — affected >=0 <0.2.0

## Details
Affected versions allow arbitrary caller-provided code to execute before the lifetime of `main`.

If the caller-provided code accesses particular pieces of the standard library that require an initialized Rust runtime, such as `std::io` or `std::thread`, these may not behave as documented. Panics are likely; UB is possible.

The flaw was corrected by enforcing that only code written within the `inventory` crate, which is guaranteed not to access runtime-dependent parts of the standard library, runs before `main`. Caller-provided code is restricted to running at compile time.

## References
- https://github.com/dtolnay/inventory/pull/43
- https://github.com/dtolnay/inventory/commit/b853350a3800e38d2cb9950355b80bc8b8d3959c
- https://github.com/dtolnay/inventory
- https://rustsec.org/advisories/RUSTSEC-2023-0057.html
