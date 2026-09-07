# [M] XSS via Angular Expression in ag-grid

## Summary
Severity: Medium
Advisory: GHSA-wfw3-rgfr-6g67
CVE: CVE-2017-16009
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-wfw3-rgfr-6g67
Type: github-advisory

## Affected
- npm: `ag-grid` — affected >=0

## Details
Affected versions of `ag-grid` are vulnerable to Cross-site Scripting (XSS) via Angular Expressions, if used in combination with AngularJS.


## Recommendation

Avoid using `ag-grid` in combination with AngularJS until a fix is available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16009
- https://github.com/ceolter/ag-grid/issues/1287
- https://github.com/ag-grid/ag-grid
- https://spring.io/blog/2016/01/28/angularjs-escaping-the-expression-sandbox-for-xss
