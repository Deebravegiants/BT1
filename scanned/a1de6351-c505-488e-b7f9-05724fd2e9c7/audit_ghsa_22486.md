# [M] web2py exposure of sensitive information

## Summary
Severity: Medium
Advisory: GHSA-jr83-vr4j-mp6p
CVE: CVE-2016-3954
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-jr83-vr4j-mp6p
Type: github-advisory

## Affected
- PyPI: `web2py` — affected >=0 <2.14.2

## Details
web2py before 2.14.2 allows remote attackers to obtain the session_cookie_key value via a direct request to examples/simple_examples/status.  NOTE: this issue can be leveraged by remote attackers to execute arbitrary code using CVE-2016-3957.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3954
- https://github.com/web2py/web2py/commit/0820926b500a321060ef6a76ce89fd35a252f8b0
- https://devco.re/blog/2017/01/03/web2py-unserialize-code-execution-CVE-2016-3957
- https://github.com/web2py/web2py
- https://usn.ubuntu.com/4030-1
