# [M] Documenso 2.17.0 PDF Route Ignores Document Visibility

## Summary
Severity: Medium
Advisory: CVE-2026-85697
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85697
Type: osv

## Details
Documenso 2.17.0 contains an access control vulnerability in the PDF-serving endpoint that fails to validate document visibility settings. Attackers with low privileges can read restricted documents within their team or cross-tenant by leveraging missing ownership validation on document data identifiers.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85697.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85697
- https://www.vulncheck.com/advisories/documenso-2.17.0-pdf-route-ignores-document-visibility
- https://github.com/documenso/documenso/issues/3112
- https://github.com/documenso/documenso
- https://github.com/documenso/documenso/blob/v2.17.0/apps/remix/server/api/files/files.helpers.ts
