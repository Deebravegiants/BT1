# [M] Volmarg Personal Management System Path Traversal via get-file Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-40526
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-40526
Type: osv

## Details
Volmarg Personal Management System contains a path traversal vulnerability that allows authenticated attackers to read arbitrary files by supplying absolute filesystem paths to the GET /public/get-file/{path} endpoint. The path route parameter is passed directly to file_get_contents() without canonicalization against a permitted base directory, enabling attackers to retrieve sensitive files accessible to the PHP-FPM worker process without using directory traversal sequences.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40526.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40526
- https://www.vulncheck.com/advisories/volmarg-personal-management-system-path-traversal-via-get-file-endpoint
- https://github.com/Volmarg/personal-management-system/commit/a0443570e105ed4835ce57f3c0a3e33d5b77418c
- https://github.com/Volmarg/personal-management-system/commit/fb9d3679d5b28977ef59e61c3eed42bec602ed8b
- https://github.com/Volmarg/personal-management-system
