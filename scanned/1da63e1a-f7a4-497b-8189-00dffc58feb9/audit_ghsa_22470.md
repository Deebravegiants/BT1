# [M] qlib Deserialization of Untrusted Data vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hjr4-fhgp-23g9
CVE: CVE-2021-23338
CWE: CWE-502, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hjr4-fhgp-23g9
Type: github-advisory

## Affected
- PyPI: `pyqlib` — affected >=0 <0.7.0

## Details
This affects all versions of package qlib. The workflow function in cli part of qlib was using an unsafe YAML load function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23338
- https://github.com/418sec/huntr/pull/1329
- https://github.com/microsoft/qlib
- https://github.com/pypa/advisory-database/tree/main/vulns/pyqlib/PYSEC-2021-86.yaml
- https://security.snyk.io/vuln/SNYK-PYTHON-PYQLIB-1085990
- https://snyk.io/vuln/SNYK-PYTHON-QLIB-1054635
