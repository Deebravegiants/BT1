# [H] Dangling reference in `access::Map` with Constant

## Summary
Severity: High
Advisory: GHSA-9pqx-g3jh-qpqq
CVE: CVE-2020-35711
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9pqx-g3jh-qpqq
Type: github-advisory

## Affected
- crates.io: `arc-swap` — affected >=0.4.2 <0.4.8
- crates.io: `arc-swap` — affected >=1.0.0 <1.1.0

## Details
An issue has been discovered in the arc-swap crate before 0.4.8 (and 1.x before 1.1.0) for Rust. Use of arc_swap::access::Map with the Constant test helper (or with a user-supplied implementation of the Access trait) could sometimes lead to dangling references being returned by the map.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35711
- https://github.com/vorner/arc-swap/issues/45
- https://github.com/vorner/arc-swap
- https://rustsec.org/advisories/RUSTSEC-2020-0091.html
