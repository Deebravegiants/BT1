# [H] Data races in toolshed

## Summary
Severity: High
Advisory: GHSA-2r6q-6c8c-g762
CVE: CVE-2020-36456
CWE: CWE-362, CWE-77
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-2r6q-6c8c-g762
Type: github-advisory

## Affected
- crates.io: `toolshed` — affected >=0

## Details
An issue was discovered in the toolshed crate through 2020-11-15 for Rust. In CopyCell<T>, the Send trait lacks bounds on the contained type.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36456
- https://github.com/ratel-rust/toolshed/issues/12
- https://github.com/ratel-rust/toolshed
- https://rustsec.org/advisories/RUSTSEC-2020-0136.html
