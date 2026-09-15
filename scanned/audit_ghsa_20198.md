# [M] Optional `Deserialize` implementations lacking validation

## Summary
Severity: Medium
Advisory: GHSA-jf5h-cf95-w759
Ecosystem: crates.io
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-jf5h-cf95-w759
Type: github-advisory

## Affected
- crates.io: `raw-cpuid` — affected >=3.1.0 <9.1.1

## Details
When activating the non-default feature `serialize`, most structs implement
`serde::Deserialize` without sufficient validation. This allows breaking
invariants in safe code, leading to:

* Undefined behavior in `as_string()` methods (which use
  `std::str::from_utf8_unchecked()` internally).
* Panics due to failed assertions.

See https://github.com/gz/rust-cpuid/issues/43.

## References
- https://github.com/gz/rust-cpuid/issues/43
- https://github.com/gz/rust-cpuid
- https://rustsec.org/advisories/RUSTSEC-2021-0089.html
