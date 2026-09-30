# [M] req may send an unintended request when a malformed URL is provided

## Summary
Severity: Medium
Advisory: GHSA-cj55-gc7m-wvcq
CVE: CVE-2024-45258
CWE: CWE-20, CWE-918, CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-26
Source: https://github.com/advisories/GHSA-cj55-gc7m-wvcq
Type: github-advisory

## Affected
- Go: `github.com/imroc/req/v3` — affected >=0 <3.43.4
- Go: `github.com/imroc/req` — affected >=0 <3.43.4
- Go: `github.com/imroc/req/v2` — affected >=0 <3.43.4

## Details
The `req` library is a widely used HTTP library in Go. However, it does not handle malformed URLs effectively. As a result, after parsing a malformed URL, the library may send HTTP requests to unexpected destinations, potentially leading to security vulnerabilities or unintended behavior in applications relying on this library for handling HTTP requests.

Despite developers potentially utilizing the `net/url` library to parse malformed URLs and implement blocklists to prevent HTTP requests to listed URLs, inconsistencies exist between how the `net/url` and `req` libraries parse URLs. These discrepancies can lead to the failure of defensive strategies, resulting in potential security threats such as Server-Side Request Forgery (SSRF) and Remote Code Execution (RCE).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45258
- https://github.com/imroc/req/commit/04e3ece5b380ecad9da3551c449f1b8a9aa76d3d
- https://github.com/imroc/req
- https://github.com/imroc/req/compare/v3.43.3...v3.43.4
- https://pkg.go.dev/vuln/GO-2024-3098
