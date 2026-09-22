# [M] PDFio < 1.6.5 Dangling Pointer via Dictionary String-Formatting

## Summary
Severity: Medium
Advisory: CVE-2026-77220
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-77220
Type: osv

## Details
PDFio before 1.6.5 contains a dangling pointer vulnerability in the dictionary string-formatting function that stores a pointer to a stack-local buffer in the document dictionary without copying the string value. In multi-threaded or pooled-request environments, attackers or concurrent users can trigger stack memory reuse across requests, causing cross-tenant document content corruption by silently overwriting one caller's dictionary string values with another caller's data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77220.json
- https://github.com/michaelrsweet/pdfio/releases/tag/v1.6.5
- https://nvd.nist.gov/vuln/detail/CVE-2026-77220
- https://www.vulncheck.com/advisories/pdfio-dangling-pointer-via-dictionary-string-formatting
- https://github.com/michaelrsweet/pdfio/commit/22b9afc800c5833f9e851e35938972bd4c76a357
- https://github.com/michaelrsweet/pdfio
