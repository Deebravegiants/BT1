# [M] Cross-site Scripting in python-cjson

## Summary
Severity: Medium
Advisory: GHSA-95jp-77w6-qj52
CVE: CVE-2009-4924
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-12-06
Source: https://github.com/advisories/GHSA-95jp-77w6-qj52
Type: github-advisory

## Affected
- PyPI: `python-cjson` — affected >=0 <1.1.0

## Details
Python-cjson 1.0.5 does not properly handle a ['/'] argument to cjson.encode, which makes it easier for remote attackers to conduct certain cross-site scripting (XSS) attacks involving Firefox and the end tag of a SCRIPT element.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-4924
- https://github.com/AGProjects/python-cjson
- https://github.com/advisories/GHSA-95jp-77w6-qj52
- https://github.com/pypa/advisory-database/tree/main/vulns/python-cjson/PYSEC-2010-26.yaml
- https://github.com/pypa/advisory-db/tree/main/vulns/python-cjson/PYSEC-2010-26.yaml
- http://pypi.python.org/pypi/python-cjson
- http://t3.dotgnu.info/blog/insecurity/quotes-dont-help.html
