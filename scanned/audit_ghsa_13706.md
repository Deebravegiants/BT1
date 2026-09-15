# [M] github.com/go-resty/resty/v2 HTTP request body disclosure

## Summary
Severity: Medium
Advisory: GHSA-xwh9-gc39-5298
CVE: CVE-2023-45286
CWE: CWE-200, CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-11-28
Source: https://github.com/advisories/GHSA-xwh9-gc39-5298
Type: github-advisory

## Affected
- Go: `github.com/go-resty/resty/v2` — affected >=2.10.0 <2.11.0

## Details
A race condition in go-resty can result in HTTP request body disclosure across requests.

This condition can be triggered by calling sync.Pool.Put with the same *bytes.Buffer more than once, when request retries are enabled and a retry occurs. The call to sync.Pool.Get will then return a bytes.Buffer that hasn't had bytes.Buffer.Reset called on it. This dirty buffer will contain the HTTP request body from an unrelated request, and go-resty will append the current HTTP request body to it, sending two bodies in one request.

The sync.Pool in question is defined at package level scope, so a completely unrelated server could receive the request body.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-45286
- https://github.com/go-resty/resty/issues/739
- https://github.com/go-resty/resty/issues/743
- https://github.com/go-resty/resty/pull/745
- https://github.com/go-resty/resty/commit/577fed8730d79f583eb48dfc81674164e1fc471e
- https://github.com/go-resty/resty
- https://github.com/go-resty/resty/releases/tag/v2.11.0
- https://pkg.go.dev/vuln/GO-2023-2328
