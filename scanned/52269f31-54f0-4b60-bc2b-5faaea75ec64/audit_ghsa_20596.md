# [M] NumPy Buffer Overflow (Disputed)

## Summary
Severity: Medium
Advisory: GHSA-6p56-wp2h-9hxr
CVE: CVE-2021-33430
CWE: CWE-120
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-07
Source: https://github.com/advisories/GHSA-6p56-wp2h-9hxr
Type: github-advisory

## Affected
- PyPI: `numpy` — affected >=1.9.0 <1.21

## Details
A Buffer Overflow vulnerability exists in NumPy 1.9.x in the PyArray_NewFromDescr_int function of ctors.c when specifying arrays of large dimensions (over 32) from Python code, which could let a malicious user cause a Denial of Service.

NOTE: The vendor does not agree this is a vulnerability; In (very limited) circumstances a user may be able provoke the buffer overflow, the user is most likely already privileged to at least provoke denial of service by exhausting memory. Triggering this further requires the use of uncommon API (complicated structured dtypes), which is very unlikely to be available to an unprivileged user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33430
- https://github.com/numpy/numpy/issues/18939
- https://github.com/numpy/numpy/commit/ae317fd9ff3e79c0eac357d723bfc29cbd625f2e
- https://github.com/numpy/numpy
- https://github.com/pypa/advisory-database/tree/main/vulns/numpy/PYSEC-2021-854.yaml
