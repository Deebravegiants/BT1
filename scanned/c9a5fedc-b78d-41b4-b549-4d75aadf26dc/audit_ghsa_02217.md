# [H] Out of bounds read in ordnung

## Summary
Severity: High
Advisory: GHSA-qrwc-jxf5-g8x6
CVE: CVE-2020-35890
CWE: CWE-125
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-qrwc-jxf5-g8x6
Type: github-advisory

## Affected
- crates.io: `ordnung` — affected >=0

## Details
An issue was discovered in the ordnung crate through version 0.0.1 for Rust. compact::Vec violates memory safety via out-of-bounds access for large capacity.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35890
- https://github.com/maciejhirsz/ordnung/issues/8
- https://github.com/maciejhirsz/ordnung
- https://rustsec.org/advisories/RUSTSEC-2020-0038.html
