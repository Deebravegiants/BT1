# [H] Python Charmers Future denial of service vulnerability

## Summary
Severity: High
Advisory: GHSA-v3c5-jqr6-7qm8
CVE: CVE-2022-40899
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-23
Source: https://github.com/advisories/GHSA-v3c5-jqr6-7qm8
Type: github-advisory

## Affected
- PyPI: `future` — affected >=0 <0.18.3

## Details
An issue discovered in Python Charmers Future 0.18.2 and earlier allows remote attackers to cause a denial of service via crafted Set-Cookie header from malicious web server. This issue has been patched in version 0.18.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40899
- https://github.com/PythonCharmers/python-future/pull/610
- https://github.com/python/cpython/pull/17157
- https://github.com/PythonCharmers/python-future/commit/c91d70b34ef0402aef3e9d04364ba98509dca76f
- https://github.com/PythonCharmers/python-future
- https://github.com/PythonCharmers/python-future/blob/master/src/future/backports/http/cookiejar.py#L215
- https://github.com/pypa/advisory-database/tree/main/vulns/future/PYSEC-2022-42991.yaml
- https://pypi.org/project/future
- https://pyup.io/posts/pyup-discovers-redos-vulnerabilities-in-top-python-packages
