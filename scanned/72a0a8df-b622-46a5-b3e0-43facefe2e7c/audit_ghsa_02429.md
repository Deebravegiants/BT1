# [C] Out of bounds read in bra

## Summary
Severity: Critical
Advisory: GHSA-j8qq-58cr-8cc7
CVE: CVE-2021-25905
CWE: CWE-125, CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-j8qq-58cr-8cc7
Type: github-advisory

## Affected
- crates.io: `bra` — affected >=0 <0.1.1

## Details
Buffered Random Access (BRA) provides easy random memory access to a sequential source of data in Rust. This is achieved by greedily retaining all memory read from a given source. Buffered Random Access (BRA) provides easy random memory access to a sequential source of data in Rust. An issue was discovered in the bra crate before 0.1.1 for Rust. It lacks soundness because it can read uninitialized memory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25905
- https://github.com/Enet4/bra-rs/issues/1
- https://github.com/Enet4/bra-rs/commit/aabf5562f8c6374ab30f615b28e0cff9b5c79e5f
- https://github.com/Enet4/bra-rs
- https://rustsec.org/advisories/RUSTSEC-2021-0008.html
