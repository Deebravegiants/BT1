# [M] Hive has Double-free and Use After Free Vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-j8cj-hw74-64jv
CWE: CWE-415, CWE-416
Ecosystem: crates.io
Published: 2026-02-28
Source: https://github.com/advisories/GHSA-j8cj-hw74-64jv
Type: github-advisory

## Affected
- crates.io: `hivex` — affected >=0.2.0 <0.2.1

## Details
`Drop` implementation for `Hive` did perform free, but so did `Hive::close`, which, at the end of the scope performed `Drop`, therefore triggering double-free.

Additionally, function `Hive::from_handle` was not marked as unsafe, making it, in combination with `as_handle` easy to clone and trigger double-free in safe code or triggering UB when using invalid pointer.

## References
- https://codeberg.org/1millibyte/toolsnt/commit/f4c7a0d1fc4a08ce40bb76e447a69a6f383a916e
- https://codeberg.org/1millibyte/toolsnt/issues/18
- https://docs.rs/crate/hivex
- https://docs.rs/crate/hivex/0.2.1/source
- https://rustsec.org/advisories/RUSTSEC-2026-0029.html
