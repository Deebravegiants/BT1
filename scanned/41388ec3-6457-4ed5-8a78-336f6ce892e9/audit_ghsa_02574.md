# [H] Uninitialized memory access in toodee

## Summary
Severity: High
Advisory: GHSA-xm9m-2vj8-fmfr
CVE: CVE-2021-28029
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-xm9m-2vj8-fmfr
Type: github-advisory

## Affected
- crates.io: `toodee` — affected >=0 <0.3.0

## Details
An issue was discovered in the toodee crate before 0.3.0 for Rust. The row-insertion feature allows attackers to read the contents of uninitialized memory locations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28029
- https://github.com/antonmarsden/toodee/issues/13
- https://github.com/antonmarsden/toodee
- https://rustsec.org/advisories/RUSTSEC-2021-0028.html
