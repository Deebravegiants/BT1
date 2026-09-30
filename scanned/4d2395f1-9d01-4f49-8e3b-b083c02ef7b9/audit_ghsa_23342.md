# [H] PyAMF vulnerable to XML external entity (XXE)

## Summary
Severity: High
Advisory: GHSA-m7m4-4vm8-55wg
CVE: CVE-2015-8549
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m7m4-4vm8-55wg
Type: github-advisory

## Affected
- PyPI: `pyamf` — affected >=0 <0.8.0

## Details
PyAMF provides Action Message Format (AMF) support for Python that is compatible with the Adobe Flash Player. It includes integration with Python web frameworks like Django, Pylons, Twisted, SQLAlchemy, web2py and more. XML external entity (XXE) vulnerability in PyAMF before 0.8.0 allows remote attackers to cause a denial of service or read arbitrary files via a crafted Action Message Format (AMF) payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8549
- https://github.com/hydralabs/pyamf/pull/58
- https://github.com/advisories/GHSA-m7m4-4vm8-55wg
- https://github.com/hydralabs/pyamf
- https://github.com/hydralabs/pyamf/releases/tag/v0.8.0
- https://github.com/pypa/advisory-database/tree/main/vulns/pyamf/PYSEC-2020-339.yaml
- https://pypi.org/project/pyamf
- http://www.ocert.org/advisories/ocert-2015-011.html
