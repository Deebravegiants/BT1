# [M] http-swagger XSS via PUT requests

## Summary
Severity: Medium
Advisory: GHSA-49w7-5r33-jm9m
CVE: CVE-2024-25712
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-29
Source: https://github.com/advisories/GHSA-49w7-5r33-jm9m
Type: github-advisory

## Affected
- Go: `github.com/swaggo/http-swagger` — affected >=0 <1.2.6

## Details
http-swagger before 1.2.6 allows XSS via PUT requests, because a file that has been uploaded (via httpSwagger.WrapHandler and *webdav.memFile) can subsequently be accessed via a GET request. NOTE: this is independently fixable with respect to CVE-2022-24863, because (if a solution continued to allow PUT requests) large files could have been blocked without blocking JavaScript, or JavaScript could have been blocked without blocking large files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25712
- https://github.com/swaggo/http-swagger/pull/62
- https://github.com/swaggo/http-swagger/commit/b7d83e8fba85a7a51aa7e45e8244b4173f15049e
- https://cosmosofcyberspace.github.io/improper_http_method_leads_to_xss/poc.html
- https://github.com/swaggo/http-swagger
- https://github.com/swaggo/http-swagger/releases/tag/v1.2.6
