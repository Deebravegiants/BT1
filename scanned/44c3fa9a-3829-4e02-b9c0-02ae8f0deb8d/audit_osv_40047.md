# [M] Typemill < 2.24.0 Path Traversal via ControllerApiImage::getPagemedia()

## Summary
Severity: Medium
Advisory: CVE-2026-49133
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-49133
Type: osv

## Details
Typemill before 2.24.0 contains a path traversal vulnerability that allows authenticated attackers with Author-level privileges to read arbitrary files outside the content directory by supplying traversal sequences in the path query parameter passed to Storage::getFile() with an empty folder argument. Attackers can bypass traversal-prevention controls in Storage::getFolderPath() to access sensitive files.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49133.json
- https://github.com/typemill/typemill/releases/tag/v2.24.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-49133
- https://www.vulncheck.com/advisories/typemill-path-traversal-via-controllerapiimage-getpagemedia
- https://github.com/typemill/typemill/commit/bfbb27001acd5c56ad62166dbefe6a59798cf1c0
- https://github.com/typemill/typemill
