# [C] Loading a bgzip block can write out of bounds if size overflows.

## Summary
Severity: Critical
Advisory: GHSA-cpqj-r29q-chrh
CVE: CVE-2021-28027
CWE: CWE-191
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cpqj-r29q-chrh
Type: github-advisory

## Affected
- crates.io: `bam` — affected >=0 <0.1.3

## Details
An issue was discovered in the bam crate before 0.1.3 for Rust. There is an integer underflow and out-of-bounds write during the loading of a bgzip block.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28027
- https://gitlab.com/tprodanov/bam
- https://gitlab.com/tprodanov/bam/-/issues/4
- https://rustsec.org/advisories/RUSTSEC-2021-0027.html
