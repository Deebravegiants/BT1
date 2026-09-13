# [H] Langflow - Path Traversal Arbitrary File Write via upload_user_file

## Summary
Severity: High
Advisory: CVE-2026-5027
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-5027
Type: osv

## Details
The 'POST /api/v2/files' endpoint does not sanitize the 'filename' parameter from the multipart form data, allowing an attacker to write files to arbitrary locations on the filesystem using path traversal sequences ('../').

## References
- https://www.tenable.com/security/research/tra-2026-26
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5027.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5027
- https://github.com/langflow-ai/langflow
