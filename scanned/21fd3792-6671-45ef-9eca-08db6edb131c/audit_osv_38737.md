# [M] OpenClaw < 2026.4.8 - Workspace-Only Filesystem Policy Bypass via docx upload_file/upload_image

## Summary
Severity: Medium
Advisory: CVE-2026-41911
Aliases: GHSA-5fc7-f62m-8983
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-28
Source: https://osv.dev/vulnerability/CVE-2026-41911
Type: osv

## Details
OpenClaw before 2026.4.8 contains a filesystem policy bypass vulnerability in docx upload processing that allows local file reads outside workspace boundaries. Attackers can exploit upload_file and upload_image endpoints to access files beyond the intended workspace-only filesystem policy.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41911.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-5fc7-f62m-8983
- https://nvd.nist.gov/vuln/detail/CVE-2026-41911
- https://www.vulncheck.com/advisories/openclaw-workspace-only-filesystem-policy-bypass-via-docx-upload-file-upload-image
- https://github.com/openclaw/openclaw/commit/d7c3210cd6f5fdfdc1beff4c9541673e814354d5
