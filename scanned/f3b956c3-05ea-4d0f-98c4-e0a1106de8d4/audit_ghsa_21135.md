# [H] Codecov does not sanitize gcov arguments

## Summary
Severity: High
Advisory: GHSA-h3qr-fjhm-jphw
CVE: CVE-2019-10800
CWE: CWE-88
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-07-14
Source: https://github.com/advisories/GHSA-h3qr-fjhm-jphw
Type: github-advisory

## Affected
- PyPI: `codecov` — affected >=0 <2.0.16

## Details
This affects the package codecov before 2.0.16. The vulnerability occurs due to not sanitizing gcov arguments before being being provided to the popen method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10800
- https://github.com/codecov/codecov-python/commit/2a80aa434f74feb31242b6f213b75ce63ae97902
- https://github.com/advisories/GHSA-h3qr-fjhm-jphw
- https://github.com/codecov/codecov-python
- https://github.com/pypa/advisory-database/tree/main/vulns/codecov/PYSEC-2022-238.yaml
- https://snyk.io/vuln/SNYK-PYTHON-CODECOV-552149
