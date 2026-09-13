# [C] ImpressCMS Authenticated RCE via PHP Custom Tag eval()

## Summary
Severity: Critical
Advisory: CVE-2026-73679
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-73679
Type: osv

## Details
ImpressCMS contains an authenticated remote code execution vulnerability in the custom tag module that allows authenticated administrators to execute arbitrary PHP code by storing a malicious payload in a custom tag with PHP type enabled. The application decodes HTML-encoded content via undoHtmlSpecialChars() before passing it to eval() in the renderWithPhp() method, bypassing HTML Purifier sanitization, and the payload is triggered on every frontend page load through the preload event system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73679.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73679
- https://www.vulncheck.com/advisories/impresscms-authenticated-rce-via-php-custom-tag-eval
- https://github.com/ImpressCMS/impresscms
- https://github.com/DevVaibhav07/VULN-POC/blob/main/ImpressCMSRCCE.md
