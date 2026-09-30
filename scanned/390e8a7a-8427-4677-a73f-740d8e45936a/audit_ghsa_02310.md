# [M] Reference counting error in pyo3

## Summary
Severity: Medium
Advisory: GHSA-2vx6-fcw6-hpr6
CVE: CVE-2020-35917
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-2vx6-fcw6-hpr6
Type: github-advisory

## Affected
- crates.io: `pyo3` — affected >=0.12.0 <0.12.4

## Details
An issue was discovered in the pyo3 crate before 0.12.4 for Rust. There is a reference-counting error and use-after-free in From<Py<T>>.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35917
- https://github.com/PyO3/pyo3/pull/1297
- https://github.com/PyO3/pyo3/commit/8f81f595dd770b586c7ca7195b42004a6c976eb9
- https://github.com/PyO3/pyo3
- https://rustsec.org/advisories/RUSTSEC-2020-0074.html
