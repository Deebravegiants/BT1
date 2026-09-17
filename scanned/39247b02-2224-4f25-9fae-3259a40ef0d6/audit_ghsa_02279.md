# [H] Use after free in libpulse-binding

## Summary
Severity: High
Advisory: GHSA-ghpq-vjxw-ch5w
CWE: CWE-416
Ecosystem: crates.io
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-ghpq-vjxw-ch5w
Type: github-advisory

## Affected
- crates.io: `libpulse-binding` — affected >=0 <1.2.1

## Details
### Overview

Version 1.2.1 of the `libpulse-binding` Rust crate, released on the 15th of June 2018, fixed a pair of use-after-free issues with the objects returned by the `get_format_info` and `get_context` methods of `Stream` objects. These objects were mistakenly being constructed without setting an important flag to prevent destruction of the underlying C objects they reference upon their own destruction.

This advisory is being written retrospectively, having previously only been noted in the changelog. No CVE assignment was sought.

### Patches

Users are required to update to version 1.2.1 or newer.

Versions older than 1.2.1 have been yanked from crates.io. This was believed to have already been done at the time of the 1.2.1 release, but upon double checking now they were found to still be available, so has been done now (22nd October 2020).

## References
- https://github.com/jnqnfe/pulse-binding-rust/security/advisories/GHSA-ghpq-vjxw-ch5w
- https://github.com/jnqnfe/pulse-binding-rust
- https://rustsec.org/advisories/RUSTSEC-2018-0021.html
