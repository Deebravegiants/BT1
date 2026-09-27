# [H] IDOR in Prospero Flow CRM allows cross-tenant product disclosure and hijacking

## Summary
Severity: High
Advisory: CVE-2026-19734
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-19734
Type: osv

## Details
Missing Authorization and Authorization Bypass Through User-Controlled Key in the product management component in Roskus Prospero Flow CRM before 5.4.7 allows authenticated users of any company to read the full sensitive data (price, cost, stock, SKU, and barcode) of another company's product and to hijack that product by reassigning its company_id, via the product's numeric identifier, because `ProductUpdateController` did not extend `MainController` and therefore required no authentication check on the read endpoint, and `ProductRepository::save()` retrieved the record via `Product::find($data['id'])` without constraining the query to the authenticated user's company before overwriting its company_id.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19734.json
- https://github.com/Roskus/prospero-flow-crm/releases/tag/v5.5.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-19734
- https://github.com/Roskus/prospero-flow-crm/commit/f36c2a115f4c28c82181f1798c01582ae953b932
- https://github.com/Roskus/prospero-flow-crm
- https://secur0.com/en/cna/cve-list/cve-2026-19734-idor-in-prospero-flow-crm-allows-cross-tenant-product-disclosure-and-hijacking
