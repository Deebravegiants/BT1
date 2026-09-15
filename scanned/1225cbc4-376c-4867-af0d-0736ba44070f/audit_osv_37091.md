# [C] FreeScout 1.8.206 Patch Bypass for CVE-2026-27636 via Zero-Width Space Character Leads to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-28289
Aliases: GHSA-5gpc-65p8-ffwp
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-03
Source: https://osv.dev/vulnerability/CVE-2026-28289
Type: osv

## Details
FreeScout is a free help desk and shared inbox built with PHP's Laravel framework. A patch bypass vulnerability for CVE-2026-27636 in FreeScout 1.8.206 and earlier allows any authenticated user with file upload permissions to achieve Remote Code Execution (RCE) on the server by uploading a malicious .htaccess file using a zero-width space character prefix to bypass the security check. The vulnerability exists in the sanitizeUploadedFileName() function in app/Http/Helper.php. The function contains a Time-of-Check to Time-of-Use (TOCTOU) flaw where the dot-prefix check occurs before sanitization removes invisible characters. This vulnerability is fixed in 1.8.207.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28289.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-5gpc-65p8-ffwp
- https://nvd.nist.gov/vuln/detail/CVE-2026-28289
- https://github.com/freescout-help-desk/freescout/commit/f7bc16c56a6b13c06da52ad51fd666546b40818f
- https://www.ox.security/blog/freescout-rce-cve-2026-28289/
