# [H] Off-by-one error in simple-slab

## Summary
Severity: High
Advisory: GHSA-hqc8-j86x-2764
CVE: CVE-2020-35893
CWE: CWE-193
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-hqc8-j86x-2764
Type: github-advisory

## Affected
- crates.io: `simple-slab` — affected >=0 <0.3.3

## Details
An issue was discovered in the simple-slab crate before 0.3.3 for Rust. remove() has an off-by-one error, causing memory leakage and a drop of uninitialized memory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35893
- https://github.com/nathansizemore/simple-slab/issues/2
- https://github.com/nathansizemore/simple-slab/commit/5e0524c1db836e2192e1cd818848d96937c0b587
- https://github.com/nathansizemore/simple-slab
- https://rustsec.org/advisories/RUSTSEC-2020-0039.html
