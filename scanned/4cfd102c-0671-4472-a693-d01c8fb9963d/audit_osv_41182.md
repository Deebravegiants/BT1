# [H] OpenBMB ChatDev - Unauthenticated Path Traversal in Upload Handler Allows Arbitrary File Write and Delete

## Summary
Severity: High
Advisory: CVE-2026-58166
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58166
Type: osv

## Details
OpenBMB ChatDev through 2.2.0, fixed in commit 4fd4da6, contains a path traversal vulnerability that allows unauthenticated remote attackers to write or delete arbitrary files by supplying a malicious multipart filename in the file upload endpoint. Attackers can send a crafted filename containing path traversal sequences or an absolute path to the POST uploads session endpoint, which constructs the destination path without sanitization in save_upload_file, causing file write and cleanup operations to target attacker-chosen paths on the server filesystem.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58166.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58166
- https://www.vulncheck.com/advisories/openbmb-chatdev-unauthenticated-path-traversal-in-upload-handler-allows-arbitrary-file-write-and-delete
- https://github.com/OpenBMB/ChatDev/pull/641
- https://github.com/OpenBMB/ChatDev/commit/4fd4da603801766b14ad8788649cfc1ad21f99a6
- https://github.com/OpenBMB/ChatDev
- https://github.com/OpenBMB/ChatDev/issues/638
