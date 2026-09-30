# [M] DeepCode 1.2.0 Path Traversal via SPA Catch-All Route in main.py

## Summary
Severity: Medium
Advisory: CVE-2026-32847
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-32847
Type: osv

## Details
DeepCode through commit c991dc2 contains a path traversal vulnerability in the SPA catch-all route in new_ui/backend/main.py that allows unauthenticated attackers to read arbitrary files by supplying percent-encoded path segments to the GET /{full_path:path} endpoint. Attackers can bypass Starlette's path normalization by encoding slashes as %2F and dots as %2E%2E, causing the joined path to traverse outside FRONTEND_DIST and exposing sensitive files such as SSH private keys, TLS certificates, and application secrets with a single HTTP request.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32847.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-32847
- https://www.vulncheck.com/advisories/deepcode-path-traversal-via-spa-catch-all-route-in-main-py
- https://github.com/HKUDS/DeepCode/issues/126
- https://github.com/HKUDS/DeepCode
