# [C] web2py remote code execution via hardcoded encryption key in session.connect function

## Summary
Severity: Critical
Advisory: GHSA-q2rq-qgcf-m22w
CVE: CVE-2016-3953
CWE: CWE-798
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-q2rq-qgcf-m22w
Type: github-advisory

## Affected
- PyPI: `web2py` — affected >=0 <2.14.2

## Details
The sample web application in web2py before 2.14.2 might allow remote attackers to execute arbitrary code via vectors involving use of a hardcoded encryption key when calling the `session.connect` function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3953
- https://github.com/web2py/web2py/issues/1205
- https://github.com/web2py/web2py/commit/9706d125b42481178d2b423de245f5d2faadbf40
- https://devco.re/blog/2017/01/03/web2py-unserialize-code-execution-CVE-2016-3957
- https://github.com/web2py/web2py
- https://github.com/web2py/web2py/blob/R-2.14.1/applications/examples/models/session.py
- https://usn.ubuntu.com/4030-1
