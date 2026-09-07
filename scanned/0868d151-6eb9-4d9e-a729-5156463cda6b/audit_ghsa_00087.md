# [C] Open Redirect in url-parse

## Summary
Severity: Critical
Advisory: GHSA-pv4c-p2j5-38j4
CVE: CVE-2018-3774
CWE: CWE-425
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2018-08-13
Source: https://github.com/advisories/GHSA-pv4c-p2j5-38j4
Type: github-advisory

## Affected
- npm: `url-parse` — affected >=1.0.0 <1.4.3

## Details
Versions of `url-parse` before 1.4.3 returns the wrong hostname which could lead to Open Redirect, Server Side Request Forgery (SSRF), or Bypass Authentication Protocol vulnerabilities.


## Recommendation

Update to version 1.4.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3774
- https://github.com/unshiftio/url-parse/commit/209c296d302317268afbe19700a70c63ecbeb2d2
- https://github.com/unshiftio/url-parse/commit/53b1794e54d0711ceb52505e0f74145270570d5a
- https://github.com/unshiftio/url-parse/commit/d7b582ec1243e8024e60ac0b62d2569c939ef5de
- https://hackerone.com/reports/384029
- https://github.com/unshiftio/url-parse
- https://github.com/unshiftio/url-parse/compare/0.2.3...1.0.0
