# [H] Double free in ordnung

## Summary
Severity: High
Advisory: GHSA-4wj3-p7hj-cvx8
CVE: CVE-2020-35891
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-4wj3-p7hj-cvx8
Type: github-advisory

## Affected
- crates.io: `ordnung` — affected >=0

## Details
An issue was discovered in the ordnung crate through version 0.0.1 for Rust. compact::Vec violates memory safety via a remove() double free.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35891
- https://github.com/maciejhirsz/ordnung/issues/8
- https://github.com/maciejhirsz/ordnung
- https://rustsec.org/advisories/RUSTSEC-2020-0038.html
