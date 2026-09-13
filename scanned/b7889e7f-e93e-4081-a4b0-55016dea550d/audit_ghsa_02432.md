# [C] Use of Uninitialized Resource in libp2p-deflate

## Summary
Severity: Critical
Advisory: GHSA-gvcp-948f-8f2p
CVE: CVE-2020-36443
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-gvcp-948f-8f2p
Type: github-advisory

## Affected
- crates.io: `libp2p-deflate` — affected >=0 <0.27.1

## Details
An issue was discovered in the libp2p-deflate crate before 0.27.1 for Rust. An uninitialized buffer is passed to AsyncRead::poll_read(), which is a user-provided trait function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36443
- https://github.com/libp2p/rust-libp2p
- https://rustsec.org/advisories/RUSTSEC-2020-0123.html
