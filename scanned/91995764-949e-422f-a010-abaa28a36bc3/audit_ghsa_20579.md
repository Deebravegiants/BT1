# [C] Pointer dereference in nanorand

## Summary
Severity: Critical
Advisory: GHSA-r57r-j98g-587f
CVE: CVE-2021-45705
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-r57r-j98g-587f
Type: github-advisory

## Affected
- crates.io: `nanorand` — affected >=0.5.0 <0.6.1

## Details
An issue was discovered in the nanorand crate before 0.6.1 for Rust. There can be multiple mutable references to the same object because the TlsWyRand Deref implementation dereferences a raw pointer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45705
- https://github.com/Absolucy/nanorand-rs/issues/28
- https://github.com/Absolucy/nanorand-rs
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/nanorand/RUSTSEC-2021-0114.md
- https://rustsec.org/advisories/RUSTSEC-2021-0114.html
