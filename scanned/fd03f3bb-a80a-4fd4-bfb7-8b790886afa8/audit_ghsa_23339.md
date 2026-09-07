# [M] Improper Neutralization of Input During Web Page Generation in html5lib

## Summary
Severity: Medium
Advisory: GHSA-v9v9-xffq-rwr4
CVE: CVE-2016-9909
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-v9v9-xffq-rwr4
Type: github-advisory

## Affected
- PyPI: `html5lib` — affected >=0 <0.999999999

## Details
The serializer in html5lib before 0.99999999 might allow remote attackers to conduct cross-site scripting (XSS) attacks by leveraging mishandling of the < (less than) character in attribute values.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9909
- https://github.com/html5lib/html5lib-python/issues/11
- https://github.com/html5lib/html5lib-python/issues/12
- https://github.com/html5lib/html5lib-python/commit/9b8d8eb5afbc066b7fac9390f5ec75e5e8a7cab7
- https://github.com/advisories/GHSA-v9v9-xffq-rwr4
- https://github.com/html5lib/html5lib-python
- https://github.com/pypa/advisory-database/tree/main/vulns/html5lib/PYSEC-2017-14.yaml
- https://html5lib.readthedocs.io/en/latest/changes.html#b9
- https://web.archive.org/web/20161229134056/http://www.securityfocus.com/bid/95132
- http://www.openwall.com/lists/oss-security/2016/12/06/5
- http://www.openwall.com/lists/oss-security/2016/12/08/8
