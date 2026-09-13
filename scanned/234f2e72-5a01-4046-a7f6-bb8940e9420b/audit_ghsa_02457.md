# [C] Out of bounds read in xcb

## Summary
Severity: Critical
Advisory: GHSA-2xpg-3hx4-fm9r
CVE: CVE-2021-26957
CWE: CWE-125
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-2xpg-3hx4-fm9r
Type: github-advisory

## Affected
- crates.io: `xcb` — affected >=0 <1.0.0

## Details
An issue was discovered in the xcb crate through 2021-02-04 for Rust. It has a soundness violation because there is an out-of-bounds read in xcb::xproto::change_property(), as demonstrated by a format=32 T=u8 situation where out-of-bounds bytes are sent to an X server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26957
- https://github.com/RustSec/advisory-db/issues/653
- https://github.com/rtbo/rust-xcb
- https://rustsec.org/advisories/RUSTSEC-2021-0019.html
