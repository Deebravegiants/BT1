# [M] Memory handling issues in xcb

## Summary
Severity: Medium
Advisory: GHSA-c8hq-x4mm-p6q6
CVE: CVE-2020-36205
CWE: CWE-415, CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-c8hq-x4mm-p6q6
Type: github-advisory

## Affected
- crates.io: `xcb` — affected >=0 <1.0.0

## Details
An issue was discovered in the xcb crate through 2020-12-10 for Rust. base::Error does not have soundness. Because of the public ptr field, a use-after-free or double-free can occur.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36205
- https://github.com/rtbo/rust-xcb/issues/93
- https://github.com/rust-x-bindings/rust-xcb/issues/93
- https://github.com/rtbo/rust-xcb
- https://rustsec.org/advisories/RUSTSEC-2020-0097.html
