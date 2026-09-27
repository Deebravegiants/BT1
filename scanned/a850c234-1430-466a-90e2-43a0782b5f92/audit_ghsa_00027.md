# [H] Code injection in Danijar Definitions

## Summary
Severity: High
Advisory: GHSA-v4x4-98cg-wr4g
CVE: CVE-2018-20325
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-12-26
Source: https://github.com/advisories/GHSA-v4x4-98cg-wr4g
Type: github-advisory

## Affected
- PyPI: `definitions` — affected >=0

## Details
There is a vulnerability in `load()` method in definitions/parser.py in the Danijar Hafner definitions package for Python. It can execute arbitrary python commands resulting in command execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20325
- https://github.com/danijar/definitions/issues/14
- https://github.com/advisories/GHSA-v4x4-98cg-wr4g
- https://github.com/danijar/definitions
- https://github.com/pypa/advisory-database/tree/main/vulns/definitions/PYSEC-2018-82.yaml
