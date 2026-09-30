# [M] Improper input validation in github.com/gin-gonic/gin

## Summary
Severity: Medium
Advisory: GHSA-3vp4-m3rf-835h
CVE: CVE-2023-26125
CWE: CWE-20, CWE-77
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-05-04
Source: https://github.com/advisories/GHSA-3vp4-m3rf-835h
Type: github-advisory

## Affected
- Go: `github.com/gin-gonic/gin` — affected >=0 <1.9.0

## Details
Versions of the package github.com/gin-gonic/gin before version 1.9.0 are vulnerable to Improper Input Validation by allowing an attacker to use a specially crafted request via the X-Forwarded-Prefix header, potentially leading to cache poisoning.

**Note:** Although this issue does not pose a significant threat on its own it can serve as an input vector for other more impactful vulnerabilities. However, successful exploitation may depend on the server configuration and whether the header is used in the application logic.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26125
- https://github.com/gin-gonic/gin/pull/3500
- https://github.com/gin-gonic/gin/pull/3503
- https://github.com/t0rchwo0d/gin/commit/fd9f98e70fb4107ee68c783482d231d35e60507b
- https://github.com/gin-gonic/gin
- https://github.com/gin-gonic/gin/releases/tag/v1.9.0
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMGINGONICGIN-3324285
