# [M] ERPNext: Broken Access Control on certain endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-72909
Aliases: GHSA-p577-cxv9-h82f
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72909
Type: osv

## Details
ERPNext is a free and open source Enterprise Resource Planning tool. Prior to 15.112.0 and 16.23.0, the ReceivablePayableReport prepare_conditions path in erpnext/accounts/report/accounts_receivable/accounts_receivable.py does not apply Customer and Supplier user permissions to the Payment Ledger Entry dynamic-link party field, allowing any authenticated user to read unauthorized cross-company financial data in Accounts Receivable and Accounts Payable reports. This issue is fixed in versions 15.112.0 and 16.23.0.

## References
- https://github.com/frappe/erpnext/releases/tag/v15.112.0
- https://github.com/frappe/erpnext/releases/tag/v16.23.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72909.json
- https://github.com/frappe/erpnext/security/advisories/GHSA-p577-cxv9-h82f
- https://nvd.nist.gov/vuln/detail/CVE-2026-72909
- https://github.com/frappe/erpnext/commit/b05abbc53b3655b02db17ba2e8165519f195c1c2
- https://github.com/frappe/erpnext/commit/c03a66a1bf48a53c42d01c9d936d9b22aa013e11
- https://github.com/frappe/erpnext/pull/55696
