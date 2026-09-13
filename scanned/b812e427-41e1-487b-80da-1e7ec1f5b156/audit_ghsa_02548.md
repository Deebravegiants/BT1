# [H] Dangling reference in flatbuffers

## Summary
Severity: High
Advisory: GHSA-c9h5-hf8r-m97x
CVE: CVE-2020-35864
CWE: CWE-704
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-c9h5-hf8r-m97x
Type: github-advisory

## Affected
- crates.io: `flatbuffers` — affected >=0.4.0 <2.0.0

## Details
An issue was discovered in the flatbuffers crate through 2020-04-11 for Rust. read_scalar (and read_scalar_at) can transmute values without unsafe blocks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35864
- https://github.com/google/flatbuffers/issues/5825
- https://github.com/google/flatbuffers
- https://rustsec.org/advisories/RUSTSEC-2020-0009.html
