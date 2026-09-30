# [H] DumbAssets 1.0.11 Path Traversal File Deletion via /api/delete-file

## Summary
Severity: High
Advisory: CVE-2026-45230
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-18
Source: https://osv.dev/vulnerability/CVE-2026-45230
Type: osv

## Details
DumbAssets through 1.0.11 contains a path traversal vulnerability in the POST /api/delete-file endpoint and filesToDelete array parameters that allows unauthenticated attackers to delete arbitrary files by supplying ../ sequences that bypass directory boundary validation. Attackers can exploit the optional and disabled-by-default authentication control to traverse outside the intended application directory and delete critical files such as server.js or package.json, causing complete denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45230.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45230
- https://www.vulncheck.com/advisories/dumbassets-path-traversal-file-deletion-via-api-delete-file
- https://github.com/DumbWareio/DumbAssets/pull/136
- https://github.com/DumbWareio/DumbAssets
