# [C] Heap overflow or corruption in safe-transmute

## Summary
Severity: Critical
Advisory: GHSA-2v78-j59h-fmpf
CVE: CVE-2018-21000
CWE: CWE-119
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-2v78-j59h-fmpf
Type: github-advisory

## Affected
- crates.io: `safe-transmute` — affected >=0.4.0 <0.10.1

## Details
Affected versions of this crate switched the length and capacity arguments in the Vec::from_raw_parts() constructor, which could lead to memory corruption or data leakage.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-21000
- https://github.com/nabijaczleweli/safe-transmute-rs/pull/36
- https://github.com/nabijaczleweli/safe-transmute-rs/commit/a134e06d740f9d7c287f74c0af2cd06206774364
- https://github.com/nabijaczleweli/safe-transmute-rs
- https://rustsec.org/advisories/RUSTSEC-2018-0013.html
