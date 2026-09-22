# [H] Tornado CRLF injection vulnerability

## Summary
Severity: High
Advisory: GHSA-f7fv-v9rh-prvc
CVE: CVE-2012-2374
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-f7fv-v9rh-prvc
Type: github-advisory

## Affected
- PyPI: `tornado` — affected >=0 <2.2.1

## Details
CRLF injection vulnerability in the `tornado.web.RequestHandler.set_header` function in Tornado before 2.2.1 allows remote attackers to inject arbitrary HTTP headers and conduct HTTP response splitting attacks via crafted input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-2374
- https://github.com/tornadoweb/tornado/commit/1ae91f6d58e6257e0ab49d295d8741ce1727bdb7
- https://github.com/pypa/advisory-database/tree/main/vulns/tornado/PYSEC-2012-5.yaml
- https://github.com/tornadoweb/tornado
- https://web.archive.org/web/20140720192646/http://secunia.com/advisories/49185
- https://web.archive.org/web/20200229124524/http://www.securityfocus.com/bid/53612
- http://openwall.com/lists/oss-security/2012/05/18/12
- http://www.openwall.com/lists/oss-security/2012/05/18/6
- http://www.tornadoweb.org/documentation/releases/v2.2.1.html
