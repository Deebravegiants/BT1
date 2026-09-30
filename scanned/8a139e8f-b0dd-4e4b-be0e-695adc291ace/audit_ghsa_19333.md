# [H] Arrow2 allows out of bounds access in public safe API

## Summary
Severity: High
Advisory: GHSA-wv8j-m3hx-924j
CWE: CWE-119
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-05-30
Source: https://github.com/advisories/GHSA-wv8j-m3hx-924j
Type: github-advisory

## Affected
- crates.io: `arrow2` — affected >=0

## Details
`Rows::row_unchecked()` allows out of bounds access to the underlying buffer without sufficient checks.

The arrow2 crate is no longer maintained, so there are no plans to fix this issue. Users are advised to migrate to the arrow crate, instead.

## References
- https://github.com/jorgecarleitao/arrow2
- https://rustsec.org/advisories/RUSTSEC-2025-0038.html
