# [H] json2xml Uncaught Exception vulnerability

## Summary
Severity: High
Advisory: GHSA-8rj5-2857-877j
CVE: CVE-2022-25024
CWE: CWE-248, CWE-754
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-08-23
Source: https://github.com/advisories/GHSA-8rj5-2857-877j
Type: github-advisory

## Affected
- PyPI: `json2xml` — affected >=0 <3.14.0

## Details
The json2xml package for Python allows an error in typecode decoding enabling a remote attack that can lead to an exception, causing a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25024
- https://github.com/vinitkumar/json2xml/issues/106
- https://github.com/vinitkumar/json2xml/pull/107
- https://github.com/vinitkumar/json2xml/pull/107/files
- https://github.com/vinitkumar/json2xml/commit/a9cd75b61329801b47a8fba7473bce6c85a38b9b
- https://github.com/pypa/advisory-database/tree/main/vulns/json2xml/PYSEC-2023-149.yaml
- https://github.com/vinitkumar/json2xml
- https://packaging.python.org/en/latest/guides/analyzing-pypi-package-downloads
