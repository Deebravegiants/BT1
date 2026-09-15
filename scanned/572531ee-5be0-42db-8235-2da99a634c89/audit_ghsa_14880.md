# [C] Gin mishandles a wildcard at the end of an origin string

## Summary
Severity: Critical
Advisory: GHSA-869c-j7wc-8jqv
CVE: CVE-2019-25211
CWE: CWE-346
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-06-29
Source: https://github.com/advisories/GHSA-869c-j7wc-8jqv
Type: github-advisory

## Affected
- Go: `github.com/gin-gonic/gin` — affected >=0 <1.6.0
- Go: `github.com/gin-contrib/cors` — affected >=0 <1.6.0

## Details
parseWildcardRules in Gin-Gonic CORS middleware before 1.6.0 mishandles a wildcard at the end of an origin string, e.g., https://example.community/* is allowed when the intention is that only https://example.com/* should be allowed, and http://localhost.example.com/* is allowed when the intention is that only http://localhost/* should be allowed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25211
- https://github.com/gin-contrib/cors/pull/106
- https://github.com/gin-contrib/cors/pull/57
- https://github.com/gin-contrib/cors/commit/27b723a473efd80d5a498fa9f5933c80204c850d
- https://github.com/gin-contrib/cors/compare/v1.5.0...v1.6.0
- https://github.com/gin-contrib/cors/releases/tag/v1.6.0
- https://github.com/gin-gonic/gin
- https://lists.debian.org/debian-lts-announce/2025/08/msg00024.html
