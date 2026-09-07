# [M] Cross-site Scripting in Beego

## Summary
Severity: Medium
Advisory: GHSA-c77f-4rgj-jfr4
CVE: CVE-2021-39391
CWE: CWE-64, CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-09-15
Source: https://github.com/advisories/GHSA-c77f-4rgj-jfr4
Type: github-advisory

## Affected
- Go: `github.com/beego/beego/v2` — affected >=0 <2.0.2

## Details
Cross Site Scripting (XSS) vulnerability exists in the admin panel in Beego v2.0.1 via the URI path in an HTTP request, which is activated by administrators viewing the "Request Statistics" page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-39391
- https://github.com/beego/beego/issues/4727
- https://github.com/beego/beego
