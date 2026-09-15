# [C] Unsound casting in flatbuffers

## Summary
Severity: Critical
Advisory: GHSA-gx73-2498-r55c
CVE: CVE-2019-25004
CWE: CWE-704
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-gx73-2498-r55c
Type: github-advisory

## Affected
- crates.io: `flatbuffers` — affected >=0.4.0 <0.6.1

## Details
The implementation of impl Follow for bool allows to reinterpret arbitrary bytes as a bool.

In Rust bool has stringent requirements for its in-memory representation. Use of this function allows to violate these requirements and invoke undefined behaviour in safe code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25004
- https://github.com/google/flatbuffers/issues/5530
- https://github.com/google/flatbuffers
- https://rustsec.org/advisories/RUSTSEC-2019-0028.html
