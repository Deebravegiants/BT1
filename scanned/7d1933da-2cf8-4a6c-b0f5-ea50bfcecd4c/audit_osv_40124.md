# [C] Laravel-Mediable < 7.0.0 File Upload RCE via Extension Bypass

## Summary
Severity: Critical
Advisory: CVE-2026-49972
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-49972
Type: osv

## Details
Laravel-Mediable before 7.0.0 contains a file upload vulnerability that allows unauthenticated attackers to achieve remote code execution by uploading a file with an embedded PHP extension disguised within a double extension such as shell.php.jpg. The PATHINFO_FILENAME extraction preserves the inner .php extension in the base name, and on misconfigured Apache or nginx servers that execute any filename containing .php as PHP, the stored file is interpreted as executable code while all MIME type, extension, and aggregate type validation checks pass due to the outer .jpg extension.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49972.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-49972
- https://www.vulncheck.com/advisories/laravel-mediable-file-upload-rce-via-extension-bypass
- https://github.com/plank/laravel-mediable/commit/49e3583bed13423611b3391f89e6b002571eed73
- https://github.com/plank/laravel-mediable/releases/tag/7.0.0
- https://github.com/plank/laravel-mediable
