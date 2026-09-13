# [H] macroquad vulnerable to multiple soundness issues

## Summary
Severity: High
Advisory: GHSA-gg76-hg3v-5q6c
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-05-15
Source: https://github.com/advisories/GHSA-gg76-hg3v-5q6c
Type: github-advisory

## Affected
- crates.io: `macroquad` — affected >=0

## Details
Several soundness issues have been reported. Resolving them doesn't seem to be considered a priority. In particular, unprincipled use of mutable statics is pervasive throughout the library, making it possible to cause use-after-free in safe code.

Currently, no fixed version is available.

## References
- https://github.com/not-fl3/macroquad/issues/333
- https://github.com/not-fl3/macroquad/issues/634
- https://github.com/not-fl3/macroquad/issues/723
- https://github.com/not-fl3/macroquad/issues/746
- https://github.com/not-fl3/macroquad
- https://rustsec.org/advisories/RUSTSEC-2025-0035.html
