# [H] Path traversal in github.com/valyala/fasthttp

## Summary
Severity: High
Advisory: GHSA-fx95-883v-4q4h
CVE: CVE-2022-21221
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-fx95-883v-4q4h
Type: github-advisory

## Affected
- Go: `github.com/valyala/fasthttp` — affected >=0 <1.34.0

## Details
The package github.com/valyala/fasthttp before 1.34.0 is vulnerable to Directory Traversal via the ServeFile function, due to improper sanitization. It is possible to be exploited by using a backslash %5c character in the path. **Note:** This security issue impacts Windows users only.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21221
- https://github.com/valyala/fasthttp/issues/1226
- https://github.com/valyala/fasthttp/commit/15262ecf3c602364639d465daba1e7f3604d00e8
- https://github.com/valyala/fasthttp/commit/6b5bc7bb304975147b4af68df54ac214ed2554c1
- https://github.com/valyala/fasthttp
- https://github.com/valyala/fasthttp/releases/tag/v1.34.0
- https://pkg.go.dev/vuln/GO-2022-0355
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMVALYALAFASTHTTP-2407866
