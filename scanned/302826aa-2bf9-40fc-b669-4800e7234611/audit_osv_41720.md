# [H] HeyForm has unauthenticated /api/upload endpoint that accepts arbitrary files with no auth/session/form context

## Summary
Severity: High
Advisory: CVE-2026-63429
Aliases: GHSA-432x-54v2-p7p7
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-63429
Type: osv

## Details
HeyForm is an open-source form builder. Prior to version 3.0.0-rc.9, `POST /api/upload` has no authentication guard, no global guard, no form-context validation, no `openToken` requirement, and no session cookie check. Any anonymous internet user can upload files (PDF, DOC/DOCX, XLS/XLSX, CSV, TXT, MP4, images, etc., up to 10 MB) and receive a permanent public URL on the HeyForm domain. The endpoint is used by both authenticated form creators and unauthenticated form submitters; because no form-context binding exists, every request to it is anonymously accepted. Version 3.0.0-rc.9 contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63429.json
- https://github.com/heyform/heyform/security/advisories/GHSA-432x-54v2-p7p7
- https://nvd.nist.gov/vuln/detail/CVE-2026-63429
- https://github.com/heyform/heyform/commit/092e255e9e02565de1b3c057f3dad849160952d2
