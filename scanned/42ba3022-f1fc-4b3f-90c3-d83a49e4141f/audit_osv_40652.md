# [M] LibreChat: Incomplete Fix for CVE-2024-11171 — Conversation Import Multer Instance Missing File Size Limits

## Summary
Severity: Medium
Advisory: CVE-2026-54024
Aliases: GHSA-52f6-fqwv-jccf
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-54024
Type: osv

## Details
LibreChat is an enhanced ChatGPT clone that supports multiple AI providers. Prior to 0.8.4-rc1, the fix for CVE-2024-11171 (commit bb58a2d0) added limits: { fileSize } to createMulterInstance() in the file upload routes. However, the POST /api/convos/import endpoint uses a separate multer instance that was never updated with the same limits configuration. Combined with the application-level size check being disabled by default (the CONVERSATION_IMPORT_MAX_FILE_SIZE_BYTES env var is commented out in .env.example), an authenticated user can upload arbitrarily large files to exhaust server disk space and memory. This vulnerability is fixed in 0.8.4-rc1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54024.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-52f6-fqwv-jccf
- https://nvd.nist.gov/vuln/detail/CVE-2026-54024
