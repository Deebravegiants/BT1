# [M] ncurses exposes uninitialized memory in string reading functions

## Summary
Severity: Medium
Advisory: GHSA-x77x-7mmh-cxv3
CWE: CWE-125
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-10-22
Source: https://github.com/advisories/GHSA-x77x-7mmh-cxv3
Type: github-advisory

## Affected
- crates.io: `ncurses` — affected >=0

## Details
Multiple string reading functions expose uninitialized memory by setting length to capacity when no null terminator is found.

This allows reading uninitialized memory which may contain sensitive data from previous allocations.

The ncurses-rs repository is archived and unmaintained.

## References
- https://github.com/RustSec/advisory-db/pull/2427
- https://github.com/jeaye/ncurses-rs
- https://rustsec.org/advisories/RUSTSEC-2025-0108.html
