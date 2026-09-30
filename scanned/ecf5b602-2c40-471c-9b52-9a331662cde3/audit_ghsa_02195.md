# [C] Unchecked Return Value in xcb

## Summary
Severity: Critical
Advisory: GHSA-3288-cwgw-ch86
CVE: CVE-2021-26955
CWE: CWE-252
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-3288-cwgw-ch86
Type: github-advisory

## Affected
- crates.io: `xcb` — affected >=0 <1.0.0

## Details
An issue was discovered in the xcb crate through 2021-02-04 for Rust. It has a soundness violation because xcb::xproto::GetAtomNameReply::name() calls std::str::from_utf8_unchecked() on unvalidated bytes from an X server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26955
- https://github.com/RustSec/advisory-db/issues/653
- https://github.com/rtbo/rust-xcb
- https://rustsec.org/advisories/RUSTSEC-2021-0019.html
