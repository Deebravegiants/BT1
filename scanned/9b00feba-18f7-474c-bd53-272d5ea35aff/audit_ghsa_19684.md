# [M] HTTP Proxy bypass using IPv6 Zone IDs in golang.org/x/net

## Summary
Severity: Medium
Advisory: GHSA-qxp5-gwg8-xv66
CVE: CVE-2025-22870
CWE: CWE-115, CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2025-03-12
Source: https://github.com/advisories/GHSA-qxp5-gwg8-xv66
Type: github-advisory

## Affected
- Go: `golang.org/x/net` — affected >=0 <0.36.0

## Details
Matching of hosts against proxy patterns can improperly treat an IPv6 zone ID as a hostname component. For example, when the NO_PROXY environment variable is set to "*.example.com", a request to "[::1%25.example.com]:80` will incorrectly match and not be proxied.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-22870
- https://go-review.googlesource.com/q/project:net
- https://go.dev/cl/654697
- https://go.dev/issue/71984
- https://groups.google.com/g/golang-announce/c/4t3lzH3I0eI/m/b42ImqrBAQAJ
- https://pkg.go.dev/vuln/GO-2025-3503
- https://security.netapp.com/advisory/ntap-20250509-0007
- http://www.openwall.com/lists/oss-security/2025/03/07/2
