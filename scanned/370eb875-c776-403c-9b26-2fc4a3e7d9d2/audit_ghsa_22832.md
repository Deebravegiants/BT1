# [M] Eugene Pankov Ajenti Cross-site scripting Vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-2ch8-f849-pjg3
CVE: CVE-2014-4301
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-2ch8-f849-pjg3
Type: github-advisory

## Affected
- PyPI: `ajenti` — affected >=0 <1.2.21.7

## Details
Multiple cross-site scripting (XSS) vulnerabilities in the `respond_error` function in `routing.py` in Eugene Pankov Ajenti before 1.2.21.7 allow remote attackers to inject arbitrary web script or HTML via the `PATH_INFO` to (1) `resources.js` or (2) resources.css in `ajenti:static/`, related to the traceback page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-4301
- https://github.com/Eugeny/ajenti/commit/d3fc5eb142ff16d55d158afb050af18d5ff09120
- https://github.com/Eugeny/ajenti
- https://github.com/pypa/advisory-database/tree/main/vulns/ajenti/PYSEC-2014-99.yaml
- https://web.archive.org/web/20171119051123/http://www.securityfocus.com/bid/68047
- https://www.netsparker.com/critical-xss-vulnerabilities-in-ajenti
- http://secunia.com/advisories/59177
- http://www.securityfocus.com/bid/68047
