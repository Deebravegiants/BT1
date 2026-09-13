# [H] Data races in dces

## Summary
Severity: High
Advisory: GHSA-hxw9-jxqw-jc8j
CVE: CVE-2020-36459
CWE: CWE-362, CWE-77
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-hxw9-jxqw-jc8j
Type: github-advisory

## Affected
- crates.io: `dces` — affected >=0

## Details
An issue was discovered in the dces crate through 2020-12-09 for Rust. The World type is marked as Send but lacks bounds on its EntityStore and ComponentStore. This allows non-thread safe `EntityStore` and `ComponentStore`s to be sent
across threads and cause data races.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36459
- https://gitlab.redox-os.org/redox-os/dces-rust
- https://gitlab.redox-os.org/redox-os/dces-rust/-/issues/8
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/dces/RUSTSEC-2020-0139.md
- https://rustsec.org/advisories/RUSTSEC-2020-0139.html
