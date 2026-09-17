# [H] Null pointer deference in fltk

## Summary
Severity: High
Advisory: GHSA-7qcc-g2m9-8533
CVE: CVE-2021-28307
CWE: CWE-476
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-7qcc-g2m9-8533
Type: github-advisory

## Affected
- crates.io: `fltk` — affected >=0 <0.15.3

## Details
An issue was discovered in the fltk crate before 0.15.3 for Rust. There is a NULL pointer dereference during attempted use of a non-raster image for a window icon.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28307
- https://github.com/MoAlyousef/fltk-rs/issues/519
- https://github.com/MoAlyousef/fltk-rs
- https://rustsec.org/advisories/RUSTSEC-2021-0038.html
