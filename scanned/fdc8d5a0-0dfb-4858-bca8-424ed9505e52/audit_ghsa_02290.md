# [C] Double free in alpm-rs

## Summary
Severity: Critical
Advisory: GHSA-qc4m-gc8r-mg8m
CVE: CVE-2020-35885
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-qc4m-gc8r-mg8m
Type: github-advisory

## Affected
- crates.io: `alpm-rs` — affected >=0

## Details
An issue was discovered in the alpm-rs crate through 2020-08-20 for Rust. StrcCtx performs improper memory deallocation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35885
- https://github.com/pigeonhands/rust-arch/issues/2
- https://github.com/BahNahNah/rust-arch/tree/master/alpm-rs
- https://rustsec.org/advisories/RUSTSEC-2020-0032.html
