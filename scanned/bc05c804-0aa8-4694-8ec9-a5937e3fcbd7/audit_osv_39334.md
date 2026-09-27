# [M] Heym < 0.0.21 Path Traversal File Upload via upload_file()

## Summary
Severity: Medium
Advisory: CVE-2026-45225
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-45225
Type: osv

## Details
Heym before 0.0.21 contains a path traversal vulnerability in the file upload endpoint that allows authenticated users to write attacker-controlled files to arbitrary locations by supplying a crafted filename with traversal sequences. Attackers can exploit the unvalidated filename parameter in the upload_file() handler to bypass path restrictions and write, read, or delete files outside the intended storage directory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45225.json
- https://github.com/heymrun/heym/releases/tag/v0.0.21
- https://nvd.nist.gov/vuln/detail/CVE-2026-45225
- https://www.vulncheck.com/advisories/heym-path-traversal-file-upload-via-upload-file
- https://github.com/heymrun/heym/pull/92
- https://github.com/heymrun/heym/commit/835843e6d2bf7d018cbb8e50f28f0426eaa20c84
- https://github.com/heymrun/heym
