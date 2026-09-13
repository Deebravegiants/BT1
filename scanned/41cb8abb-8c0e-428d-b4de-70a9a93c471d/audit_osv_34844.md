# [H] CVE-2025-65730

## Summary
Severity: High
Advisory: CVE-2025-65730
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-05
Source: https://osv.dev/vulnerability/CVE-2025-65730
Type: osv

## Details
Authentication Bypass via Hardcoded Credentials GoAway up to v0.62.18, fixed in 0.62.19, uses a hardcoded secret for signing JWT tokens used for authentication.

## References
- https://github.com/gian2dchris/CVEs/tree/CVE-2025-65730/CVE-2025-65730
- https://github.com/pommee/goaway/blob/v0.62.18/backend/api/auth.go#L48
- https://github.com/pommee/goaway/blob/v0.62.18/backend/api/middleware.go#L110
- https://github.com/pommee/goaway/blob/v0.62.18/backend/api/middleware.go#L15
- https://github.com/pommee/goaway/blob/v0.62.18/backend/api/middleware.go#L40
- https://github.com/pommee/goaway/blob/v0.62.18/backend/api/middleware.go#L69
- https://github.com/pommee/goaway/blob/v0.62.18/backend/api/middleware.go#L88
- https://github.com/pommee/goaway/releases/tag/v0.62.16
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65730.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65730
- https://github.com/pommee/goaway/commit/5769f8782b7453ca1c22a201b224b5ce48532f64#diff-4ddfd6cf1311ddfd45734bb1dc53bc208df69584ba92ac4f38866bd558434678L15-L40
