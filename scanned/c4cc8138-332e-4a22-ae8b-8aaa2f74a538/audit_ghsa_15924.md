# [M]  PyO3 has a risk of use-after-free in `borrowed` reads from Python weak references

## Summary
Severity: Medium
Advisory: GHSA-6jgw-rgmm-7cv6
CVE: CVE-2024-9979
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-10-15
Source: https://github.com/advisories/GHSA-6jgw-rgmm-7cv6
Type: github-advisory

## Affected
- crates.io: `pyo3` — affected >=0.22.0 <0.22.4

## Details
The family of functions to read "borrowed" values from Python weak references were fundamentally unsound, because the weak reference does itself not have ownership of the value. At any point the last strong reference could be cleared and the borrowed value would become dangling.

In PyO3 0.22.4 these functions have all been deprecated and patched to leak a strong reference as a mitigation. PyO3 0.23 will remove these functions entirely.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9979
- https://github.com/PyO3/pyo3/pull/4590
- https://access.redhat.com/security/cve/CVE-2024-9979
- https://bugzilla.redhat.com/show_bug.cgi?id=2318646
- https://crates.io/crates/pyo3
- https://github.com/PyO3/pyo3
- https://rustsec.org/advisories/RUSTSEC-2024-0378.html
