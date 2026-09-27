# [H] Unaligned memory allocation in chunky

## Summary
Severity: High
Advisory: GHSA-qg24-8xj4-gj2h
CVE: CVE-2020-36433
CWE: CWE-758
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-qg24-8xj4-gj2h
Type: github-advisory

## Affected
- crates.io: `chunky` — affected >=0

## Details
An issue was discovered in the chunky crate through 2020-08-25 for Rust. The Chunk API does not honor an alignment requirement.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36433
- https://github.com/aeplay/chunky/issues/2
- https://github.com/aeplay/chunky
- https://rustsec.org/advisories/RUSTSEC-2020-0035.html
