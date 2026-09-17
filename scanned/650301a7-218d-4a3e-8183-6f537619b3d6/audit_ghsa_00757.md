# [H] Uncontrolled resource consumption in validators Python package

## Summary
Severity: High
Advisory: GHSA-5qcg-w2cc-xffw
CVE: CVE-2019-19588
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-01-21
Source: https://github.com/advisories/GHSA-5qcg-w2cc-xffw
Type: github-advisory

## Affected
- PyPI: `validators` — affected >=0.12.2 <0.12.6

## Details
The validators package 0.12.2 through 0.12.5 for Python enters an infinite loop when validators.domain is called with a crafted domain string. This is fixed in 0.12.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19588
- https://github.com/kvesteri/validators/issues/86
- https://github.com/python-validators/validators/issues/86
- https://github.com/advisories/GHSA-5qcg-w2cc-xffw
- https://github.com/pypa/advisory-database/tree/main/vulns/validators/PYSEC-2019-134.yaml
- https://github.com/python-validators/validators
