# [C] Double free in linea

## Summary
Severity: Critical
Advisory: GHSA-j52m-489x-v634
CVE: CVE-2019-16880
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-j52m-489x-v634
Type: github-advisory

## Affected
- crates.io: `linea` — affected >=0 <0.9.4

## Details
Affected versions of this crate did not properly implements the Matrix::zip_elements method, which causes an double free when the given trait implementation might panic. This allows an attacker to corrupt or take control of the memory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16880
- https://github.com/strake/linea.rs/issues/2
- https://github.com/strake/linea.rs
- https://rustsec.org/advisories/RUSTSEC-2019-0021.html
