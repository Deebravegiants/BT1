# [H] Stirling-PDF SSRF vulnerability on /api/v1/convert/html/pdf

## Summary
Severity: High
Advisory: CVE-2025-55150
Aliases: GHSA-xw8v-9mfm-g2pm
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L)
Published: 2025-08-11
Source: https://osv.dev/vulnerability/CVE-2025-55150
Type: osv

## Details
Stirling-PDF is a locally hosted web application that performs various operations on PDF files. Prior to version 1.1.0, when using the /api/v1/convert/html/pdf endpoint to convert HTML to PDF, the backend calls a third-party tool to process it and includes a sanitizer for security sanitization which can be bypassed and result in SSRF. This issue has been patched in version 1.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55150.json
- https://github.com/Stirling-Tools/Stirling-PDF/security/advisories/GHSA-xw8v-9mfm-g2pm
- https://nvd.nist.gov/vuln/detail/CVE-2025-55150
- https://github.com/Stirling-Tools/Stirling-PDF/commit/7d6b70871bad2a3ff810825f7382c49f55293943
