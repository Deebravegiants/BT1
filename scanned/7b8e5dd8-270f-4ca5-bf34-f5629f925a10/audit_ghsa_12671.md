# [H] xml-rs vulnerable to denial of service via invalid token in XML document

## Summary
Severity: High
Advisory: GHSA-7gf7-jv65-wjmh
CVE: CVE-2023-34411
CWE: CWE-611, CWE-617
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-05
Source: https://github.com/advisories/GHSA-7gf7-jv65-wjmh
Type: github-advisory

## Affected
- crates.io: `xml-rs` — affected >=0.8.9 <0.8.14

## Details
The xml-rs crate >= 0.8.9 and < 0.8.14 for Rust and Crab allows a denial of service (panic) via an invalid <! token (such as <!DOCTYPEs/%<!A nesting) in an XML document.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34411
- https://github.com/netvl/xml-rs/pull/226
- https://github.com/00xc/xml-rs/commit/0f084d45aa53e4a27476961785f59f2bd7d59a9f
- https://github.com/netvl/xml-rs/commit/014d808be900c85a0afc5ccdfe668be040d175aa
- https://github.com/netvl/xml-rs/commit/c09549a187e62d39d40467f129e64abf32efc35c
- https://github.com/netvl/xml-rs
- https://github.com/netvl/xml-rs/compare/0.8.13...0.8.14
