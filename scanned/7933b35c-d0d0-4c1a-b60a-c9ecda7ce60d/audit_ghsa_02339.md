# [H] Out of bounds write in arenavec

## Summary
Severity: High
Advisory: GHSA-327x-39hh-65wf
CVE: CVE-2021-29930
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-327x-39hh-65wf
Type: github-advisory

## Affected
- crates.io: `arenavec` — affected >=0

## Details
An issue was discovered in the arenavec crate through 0.1.1. A drop of uninitialized memory can sometimes occur upon a panic in T::default()

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29930
- https://github.com/ibabushkin/arenavec/issues/1
- https://github.com/ibabushkin/arenavec
- https://rustsec.org/advisories/RUSTSEC-2021-0040.html
