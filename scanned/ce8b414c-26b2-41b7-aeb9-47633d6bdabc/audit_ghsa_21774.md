# [M] Buffer Copy without Checking Size of Input in NumPy

## Summary
Severity: Medium
Advisory: GHSA-f7c7-j99h-c22f
CVE: CVE-2021-41496
CWE: CWE-120
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-08
Source: https://github.com/advisories/GHSA-f7c7-j99h-c22f
Type: github-advisory

## Affected
- PyPI: `numpy` — affected >=0 <1.19

## Details
Buffer overflow in the array_from_pyobj function of fortranobject.c in NumPy < 1.19, which allows attackers to conduct a Denial of Service attacks by carefully constructing an array with negative values.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41496
- https://github.com/numpy/numpy/issues/19000
- https://github.com/numpy/numpy
- https://www.oracle.com/security-alerts/cpujul2022.html
