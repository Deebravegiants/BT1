# [M] DynFuture Drop Can Construct a Dangling Reference

## Summary
Severity: Medium
Advisory: GHSA-j3w3-p6mr-3hrh
CWE: CWE-843
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-j3w3-p6mr-3hrh
Type: github-advisory

## Affected
- crates.io: `dyn-future` — affected >=0

## Details
DynFuture is unsound because its Drop implementation transmutes a trait-object reference into unrelated reference types, which constructs an invalid reference from trait object metadata.

This issue was reproduced against `dyn-future` 3.0.4 under Miri. The crate is unmaintained.

## References
- https://github.com/rustsec/advisory-db/issues/2595
- https://github.com/xacrimon/dyn-future
- https://rustsec.org/advisories/RUSTSEC-2026-0079.html
