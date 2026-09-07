# [M] zerovec incorrectly uses `#[repr(packed)]`

## Summary
Severity: Medium
Advisory: GHSA-xrv3-jmcp-374j
CWE: CWE-120
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-07-08
Source: https://github.com/advisories/GHSA-xrv3-jmcp-374j
Type: github-advisory

## Affected
- crates.io: `zerovec` — affected >=0.10.0 <0.10.4
- crates.io: `zerovec` — affected >=0 <0.9.7

## Details
The affected versions make unsafe memory accesses under the assumption that `#[repr(packed)]` has a guaranteed field order. 

The Rust specification does not guarantee this, and https://github.com/rust-lang/rust/pull/125360 (1.80.0-beta) starts 
reordering fields of `#[repr(packed)]` structs, leading to illegal memory accesses.

The patched versions `0.9.7` and `0.10.4` use `#[repr(C, packed)]`, which guarantees field order.

## References
- https://rustsec.org/advisories/RUSTSEC-2024-0347.html
