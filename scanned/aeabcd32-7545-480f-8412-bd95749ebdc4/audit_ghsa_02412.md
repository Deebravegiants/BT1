# [H] Use after free in heapless

## Summary
Severity: High
Advisory: GHSA-qgwf-r2jj-2ccv
CVE: CVE-2020-36464
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-qgwf-r2jj-2ccv
Type: github-advisory

## Affected
- crates.io: `heapless` — affected >=0 <0.6.1

## Details
An issue was discovered in the heapless crate before 0.6.1 for Rust. The IntoIter Clone implementation clones an entire underlying Vec without considering whether it has already been partially consumed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36464
- https://github.com/japaric/heapless/issues/181
- https://github.com/japaric/heapless
- https://rustsec.org/advisories/RUSTSEC-2020-0145.html
