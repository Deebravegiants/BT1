# [H] NumPy NULL Pointer Dereference

## Summary
Severity: High
Advisory: GHSA-5545-2q6w-2gh6
CVE: CVE-2021-41495
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-08
Source: https://github.com/advisories/GHSA-5545-2q6w-2gh6
Type: github-advisory

## Affected
- PyPI: `numpy` — affected >=0 <1.19

## Details
Null Pointer Dereference vulnerability exists in numpy.sort in NumPy &lt and 1.19 in the PyArray_DescrNew function due to missing return-value validation, which allows attackers to conduct DoS attacks by repetitively creating sort arrays.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41495
- https://github.com/numpy/numpy/issues/19038
- https://github.com/advisories/GHSA-5545-2q6w-2gh6
- https://github.com/numpy/numpy
- https://github.com/pypa/advisory-database/tree/main/vulns/numpy/PYSEC-2021-856.yaml
- https://www.oracle.com/security-alerts/cpujul2022.html
