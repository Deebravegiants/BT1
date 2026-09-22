# [H] IDOR and missing authorization in Prospero Flow CRM supplier API allows cross-tenant read and modification

## Summary
Severity: High
Advisory: CVE-2026-78365
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-78365
Type: osv

## Details
Authorization Bypass Through User-Controlled Key in the supplier API in Roskus Prospero Flow CRM 4.0.0 through 5.3.1 allows any authenticated user to read and modify another company's supplier record, and to reassign it to their own company, via a PUT request to /api/supplier/{id} setting company_id in the body.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78365.json
- https://github.com/Roskus/prospero-flow-crm/releases/tag/v5.5.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-78365
- https://secur0.com/en/cna/cve-list/cve-2026-78365-idor-supplier-api-cross-tenant-update
- https://github.com/Roskus/prospero-flow-crm/commit/4a52477e6ed66afa436814c80e7bcd68670dd596
- https://github.com/Roskus/prospero-flow-crm
