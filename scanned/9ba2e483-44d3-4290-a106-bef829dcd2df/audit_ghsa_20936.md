# [H] Hertz contains path traversal via normalizePath function

## Summary
Severity: High
Advisory: GHSA-c9qr-f6c8-rgxf
CVE: CVE-2022-40082
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-29
Source: https://github.com/advisories/GHSA-c9qr-f6c8-rgxf
Type: github-advisory

## Affected
- Go: `github.com/cloudwego/hertz` — affected >=0 <0.3.1

## Details
Hertz is a a high-performance and strong-extensibility Go HTTP framework that helps developers build microservices. Versions of Hertz prior to 0.3.1 contain a path traversal vulnerability via the normalizePath function. This issue has been patched in 0.3.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40082
- https://github.com/cloudwego/hertz/issues/228
- https://github.com/cloudwego/hertz/pull/229
- https://github.com/cloudwego/hertz
- https://pkg.go.dev/vuln/GO-2022-1027
