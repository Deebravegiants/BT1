# [M] meinheld vulnerable to HTTP Request Smuggling

## Summary
Severity: Medium
Advisory: GHSA-63h2-9cc8-fc7m
CVE: CVE-2020-7658
CWE: CWE-444
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-63h2-9cc8-fc7m
Type: github-advisory

## Affected
- PyPI: `meinheld` — affected >=0 <1.0.2

## Details
meinheld prior to 1.0.2 is vulnerable to HTTP Request Smuggling. HTTP pipelining issues and request smuggling attacks might be possible due to incorrect Content-Length and Transfer encoding header parsing.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7658
- https://github.com/mopemope/meinheld/issues/111
- https://github.com/mopemope/meinheld/commit/0cfa70b2cd3800f1e4beeaef5421b156d90f0e09
- https://github.com/mopemope/meinheld/commit/3bc3e7ccd534277af955c0c92981d0aa033929a7
- https://github.com/mopemope/meinheld/commit/4155876bfd3e8fc4adad4aaa59ec3f1cefa1d2d1
- https://github.com/mopemope/meinheld
- https://github.com/mopemope/meinheld/blob/master/CHANGES.rst
- https://github.com/pypa/advisory-database/tree/main/vulns/meinheld/PYSEC-2020-239.yaml
- https://snyk.io/vuln/SNYK-PYTHON-MEINHELD-569140
