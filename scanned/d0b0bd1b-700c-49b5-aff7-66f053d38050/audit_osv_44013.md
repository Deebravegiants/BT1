# [M] IDOR and missing authorization in the Prospero Flow CRM transaction API allow cross-tenant reading of financial records

## Summary
Severity: Medium
Advisory: CVE-2026-77759
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-77759
Type: osv

## Details
Authorization Bypass Through User-Controlled Key in the transaction API in Roskus Prospero
Flow CRM 5.0.0 through 5.3.5 allows an authenticated user to read the transactions of other
companies on the same instance via an incremented identifier in GET /api/transaction/{id},
which is resolved without company scoping and without any permission check.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77759.json
- https://github.com/Roskus/prospero-flow-crm/releases/tag/v5.5.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-77759
- https://secur0.com/en/cna/cve-list/cve-2026-77759-idor-missing-authz-prospero-transaction-api
- https://github.com/Roskus/prospero-flow-crm/commit/980c35ac00e419591a8adc2d1dbcc120ea62e273
- https://github.com/Roskus/prospero-flow-crm
