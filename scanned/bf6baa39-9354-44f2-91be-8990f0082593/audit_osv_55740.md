# [C] bigint is unmaintained, use uint instead

## Summary
Severity: Critical
Advisory: RUSTSEC-2020-0025
Aliases: CVE-2020-35880, GHSA-wgx2-6432-j3fw
Ecosystem: crates.io
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-07
Source: https://osv.dev/vulnerability/RUSTSEC-2020-0025
Type: osv

## Affected
- crates.io: `bigint` — affected >=0.0.0-0

## Details
The `bigint` crate is not maintained any more and contains several known bugs (including a soundness bug);
use [`uint`](https://crates.io/crates/uint) instead.

## References
- https://crates.io/crates/bigint
- https://rustsec.org/advisories/RUSTSEC-2020-0025.html
- https://github.com/paritytech/bigint/commit/7e71521a61b009afc94c91135353102658550d42
