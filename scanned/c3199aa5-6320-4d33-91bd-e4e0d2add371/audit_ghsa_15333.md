# [M] Gorush uses deprecated TLS versions

## Summary
Severity: Medium
Advisory: GHSA-p3pf-mff8-3h47
CVE: CVE-2024-41270
CWE: CWE-327
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-08-06
Source: https://github.com/advisories/GHSA-p3pf-mff8-3h47
Type: github-advisory

## Affected
- Go: `github.com/appleboy/gorush` — affected >=0 <1.18.5

## Details
An issue discovered in the RunHTTPServer function in Gorush v1.18.4 allows attackers to intercept and manipulate data due to use of deprecated TLS version.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41270
- https://github.com/appleboy/gorush/issues/792
- https://github.com/appleboy/gorush/commit/067cb597e485e40b790a267187bf7f00730b1c4b
- https://gist.github.com/nyxfqq/cfae38fada582a0f576d154be1aeb1fc
- https://github.com/appleboy/gorush
