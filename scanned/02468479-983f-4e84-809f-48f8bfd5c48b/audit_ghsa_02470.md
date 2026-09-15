# [H] Null pointer deference in av-data

## Summary
Severity: High
Advisory: GHSA-352p-rhvq-7g78
CVE: CVE-2021-25904
CWE: CWE-476
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-352p-rhvq-7g78
Type: github-advisory

## Affected
- crates.io: `av-data` — affected >=0 <0.3.0

## Details
An issue was discovered in the av-data crate before 0.3.0 for Rust. A raw pointer is dereferenced, leading to a read of an arbitrary memory address, sometimes causing a segfault.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25904
- https://github.com/rust-av/rust-av/issues/136
- https://github.com/rust-av/rust-av
- https://rustsec.org/advisories/RUSTSEC-2021-0007.html
