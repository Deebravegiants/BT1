# [M] Perspective 5.0.0 Path Traversal via cwd_static_file_handler

## Summary
Severity: Medium
Advisory: CVE-2026-67200
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-67200
Type: osv

## Details
Perspective 5.0.0 contains a path traversal vulnerability that allows unauthenticated remote attackers to read arbitrary files from the server filesystem by including literal ../ segments in HTTP request URL paths. Attackers can bypass the insufficient query-string-stripping sanitization to traverse outside the configured asset root directory and retrieve sensitive files such as system credentials and application secrets, with results exposed cross-origin due to a wildcard Access-Control-Allow-Origin header set on all responses.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67200.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67200
- https://www.vulncheck.com/advisories/perspective-path-traversal-via-cwd-static-file-handler
- https://github.com/perspective-dev/perspective
- https://christbowel.com/blog/perspective-5-0-0-five-cves/
