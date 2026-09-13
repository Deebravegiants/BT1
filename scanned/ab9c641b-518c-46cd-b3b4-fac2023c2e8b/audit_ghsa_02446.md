# [C] Arbitrary return types in xcb

## Summary
Severity: Critical
Advisory: GHSA-mp6r-fgw2-rxfx
CVE: CVE-2021-26956
CWE: CWE-657
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-mp6r-fgw2-rxfx
Type: github-advisory

## Affected
- crates.io: `xcb` — affected >=0 <1.0.0

## Details
The function xcb::xproto::GetPropertyReply::value() returns a slice of type T where T is an unconstrained type parameter. The raw bytes received from the X11 server are interpreted as the requested type. The users of the xcb crate are advised to only call this function with the intended types. These are u8, u16, and u32.

This issue is tracked here: https://github.com/rust-x-bindings/rust-xcb/issues/95

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26956
- https://github.com/RustSec/advisory-db/issues/653
- https://github.com/rust-x-bindings/rust-xcb/issues/95
- https://github.com/rtbo/rust-xcb
- https://rustsec.org/advisories/RUSTSEC-2021-0019.html
