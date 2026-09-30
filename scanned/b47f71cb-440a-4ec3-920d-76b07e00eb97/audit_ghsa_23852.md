# [H] Numpy missing input validation

## Summary
Severity: High
Advisory: GHSA-frgw-fgh6-9g52
CVE: CVE-2017-12852
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-frgw-fgh6-9g52
Type: github-advisory

## Affected
- PyPI: `numpy` — affected >=0 <1.13.3

## Details
The numpy.pad function in Numpy 1.13.1 and older versions is missing input validation. An empty list or ndarray will stick into an infinite loop, which can allow attackers to cause a DoS attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12852
- https://github.com/numpy/numpy/issues/9560#issuecomment-322395292
- https://github.com/BT123/testcasesForMyRequest/tree/master/CVE-2017-12852
- https://github.com/advisories/GHSA-frgw-fgh6-9g52
- https://github.com/numpy/numpy
- https://github.com/numpy/numpy/releases/tag/v1.13.3
- https://github.com/pypa/advisory-database/tree/main/vulns/numpy/PYSEC-2017-1.yaml
