# [H] The PDF viewer macro allows accessing any attachment without access right checks

## Summary
Severity: High
Advisory: CVE-2024-52299
Aliases: GHSA-522m-m242-jr9p
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-11-13
Source: https://osv.dev/vulnerability/CVE-2024-52299
Type: osv

## Details
macro-pdfviewer is a PDF Viewer Macro for XWiki using Mozilla pdf.js. Any user with view right on XWiki.PDFViewerService can access any attachment stored in the wiki as the "key" that is passed to prevent this is computed incorrectly, calling skip on the digest stream doesn't update the digest. This is fixed in 2.5.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52299.json
- https://github.com/xwikisas/macro-pdfviewer/security/advisories/GHSA-522m-m242-jr9p
- https://nvd.nist.gov/vuln/detail/CVE-2024-52299
