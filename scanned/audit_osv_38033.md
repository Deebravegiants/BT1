# [H] InvoiceShelf: SSRF in Estimate PDF Rendering via Unsanitised HTML in Notes Field

## Summary
Severity: High
Advisory: CVE-2026-34365
Aliases: GHSA-pc5v-8xwc-v9xq
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34365
Type: osv

## Details
InvoiceShelf is an open-source web & mobile app that helps track expenses, payments and create professional invoices and estimates. Prior to version 2.2.0, a Server-Side Request Forgery (SSRF) vulnerability exists in the Estimate PDF generation module. User-supplied HTML in the estimate Notes field is passed unsanitised to the Dompdf rendering library, which will fetch any remote resources referenced in the markup. The vulnerability is exploitable directly via the PDF preview and customer view endpoints regardless of whether automated email attachments are enabled. This issue has been patched in version 2.2.0.

## References
- https://github.com/InvoiceShelf/InvoiceShelf/releases/tag/2.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34365.json
- https://github.com/InvoiceShelf/InvoiceShelf/security/advisories/GHSA-pc5v-8xwc-v9xq
- https://nvd.nist.gov/vuln/detail/CVE-2026-34365
