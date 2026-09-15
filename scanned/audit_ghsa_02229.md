# [H] Missing release of memory in sized-chunks

## Summary
Severity: High
Advisory: GHSA-rfgg-vccr-m46m
CVE: CVE-2020-25794
CWE: CWE-401
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-rfgg-vccr-m46m
Type: github-advisory

## Affected
- crates.io: `sized-chunks` — affected >=0 <0.6.3

## Details
An issue was discovered in the sized-chunks crate through 0.6.2 for Rust. In the Chunk implementation, clone can have a memory-safety issue upon a panic.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25794
- https://github.com/bodil/sized-chunks/issues/11
- https://github.com/bodil/sized-chunks
- https://rustsec.org/advisories/RUSTSEC-2020-0041.html
