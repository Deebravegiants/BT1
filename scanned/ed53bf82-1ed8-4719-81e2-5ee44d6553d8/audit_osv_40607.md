# [M] WebP Server Go < 0.15.0 Path Traversal via Backslash Encoding on Windows

## Summary
Severity: Medium
Advisory: CVE-2026-53779
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-53779
Type: osv

## Details
WebP Server Go through 0.14.4 contains a path traversal vulnerability on Windows that allows unauthenticated attackers to read files outside the configured IMG_PATH directory by sending requests with percent-encoded backslashes (%5C) that bypass the path.Clean() sanitization in handler/router.go. Attackers can exploit the discrepancy between Go's forward-slash-only path normalization and Windows file system APIs that treat backslashes and forward slashes as equivalent to access arbitrary files on the host filesystem accessible to the server process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53779.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53779
- https://www.vulncheck.com/advisories/webp-server-go-path-traversal-via-backslash-encoding-on-windows
- https://github.com/webp-sh/webp_server_go/pull/451
- https://github.com/webp-sh/webp_server_go/commit/eb3b5f9289b331cb639cd610b0d1c532d2cc24e0
- https://github.com/webp-sh/webp_server_go
