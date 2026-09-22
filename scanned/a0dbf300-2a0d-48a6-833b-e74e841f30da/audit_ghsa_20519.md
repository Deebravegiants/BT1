# [C] Use of Uninitialized Resource in ash.

## Summary
Severity: Critical
Advisory: GHSA-64wv-8vwp-xgw2
CVE: CVE-2021-45688
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-64wv-8vwp-xgw2
Type: github-advisory

## Affected
- crates.io: `ash` — affected >=0 <0.33.1

## Details
An issue was discovered in the ash crate before 0.33.1 for Rust. util::read_spv may read from uninitialized memory locations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45688
- https://github.com/MaikKlein/ash/issues/354
- https://github.com/ash-rs/ash/issues/354
- https://github.com/ash-rs/ash/pull/470
- https://github.com/ash-rs/ash/commit/2c98b6f384a017de031698bd623551a45f24c8f9
- https://github.com/MaikKlein/ash
- https://github.com/ash-rs/ash/compare/0.33.0...0.33.1
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/ash/RUSTSEC-2021-0090.md
- https://rustsec.org/advisories/RUSTSEC-2021-0090.html
