# [H] Double free in basic_dsp_matrix

## Summary
Severity: High
Advisory: GHSA-fjr6-hm39-4cf9
CVE: CVE-2021-25906
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-fjr6-hm39-4cf9
Type: github-advisory

## Affected
- crates.io: `basic_dsp_matrix` — affected >=0 <0.9.2

## Details
An issue was discovered in the basic_dsp_matrix crate before 0.9.2 for Rust. When a TransformContent panic occurs, a double drop can be performed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25906
- https://github.com/liebharc/basic_dsp/issues/47
- https://github.com/liebharc/basic_dsp
- https://rustsec.org/advisories/RUSTSEC-2021-0009.html
