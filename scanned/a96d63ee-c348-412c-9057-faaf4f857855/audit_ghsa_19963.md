# [H] Gin's default logger allows unsanitized input that can allow remote attackers to inject arbitrary log lines

## Summary
Severity: High
Advisory: GHSA-6vm3-jj99-7229
CVE: CVE-2020-36567
CWE: CWE-116, CWE-117
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-12-27
Source: https://github.com/advisories/GHSA-6vm3-jj99-7229
Type: github-advisory

## Affected
- Go: `github.com/gin-gonic/gin` — affected >=0 <1.6.0

## Details
Gin is a HTTP web framework written in Go (Golang). Unsanitized input in the default logger in github.com/gin-gonic/gin before v1.6.0 allows remote attackers to inject arbitrary log lines.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36567
- https://github.com/gin-gonic/gin/pull/2237
- https://github.com/gin-gonic/gin/commit/a71af9c144f9579f6dbe945341c1df37aaf09c0d
- https://github.com/gin-gonic/gin
- https://pkg.go.dev/vuln/GO-2020-0001
