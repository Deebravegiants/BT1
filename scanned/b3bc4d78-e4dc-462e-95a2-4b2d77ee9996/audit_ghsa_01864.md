# [M] Incorrect Comparison in NumPy

## Summary
Severity: Medium
Advisory: GHSA-fpfv-jqm9-f5jm
CVE: CVE-2021-34141
CWE: CWE-697
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-12-18
Source: https://github.com/advisories/GHSA-fpfv-jqm9-f5jm
Type: github-advisory

## Affected
- PyPI: `numpy` — affected >=0 <1.22

## Details
Incomplete string comparison in the numpy.core component in NumPy1.9.x, which allows attackers to fail the APIs via constructing specific string objects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-34141
- https://github.com/numpy/numpy/issues/18993
- https://github.com/numpy/numpy/issues/18993#issuecomment-1010735102
- https://github.com/advisories/GHSA-fpfv-jqm9-f5jm
- https://github.com/numpy/numpy
- https://github.com/pypa/advisory-database/tree/main/vulns/numpy/PYSEC-2021-855.yaml
- https://www.oracle.com/security-alerts/cpujul2022.html
