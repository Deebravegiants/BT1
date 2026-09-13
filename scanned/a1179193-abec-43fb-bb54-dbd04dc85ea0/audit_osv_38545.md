# [C] FrontAccounting < 2.4.20 Path Traversal RCE via attachment upload

## Summary
Severity: Critical
Advisory: CVE-2026-40521
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-40521
Type: osv

## Details
FrontAccounting before 2.4.20 contains a path traversal vulnerability in the attachment upload handler that allows authenticated attackers to execute arbitrary code by uploading files with traversal sequences in the unique_name parameter. Attackers can supply path traversal sequences ../../../shell.php to write files outside the intended attachments directory into the web root, and by uploading PHP files without extension validation, achieve remote code execution as the web server user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40521.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40521
- https://sourceforge.net/p/frontaccounting/news/2026/04/release-2420/
- https://www.vulncheck.com/advisories/frontaccounting-path-traversal-rce-via-attachment-upload
- https://github.com/FrontAccountingERP/FA/commit/701fea6848da4a02fb83d30f07a9c0473d6b7e33
- https://jivasecurity.com/writeups/frontaccounting-rce-attachment-upload-cve-2026-40521
