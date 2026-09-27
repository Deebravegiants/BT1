# [H] ERPNext: Unauthorised modification of master data due to missing validation

## Summary
Severity: High
Advisory: CVE-2026-72910
Aliases: GHSA-qpvh-75wh-j645
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72910
Type: osv

## Details
ERPNext is a free and open source Enterprise Resource Planning tool. Prior to 15.112.0 and 16.22.0, the merge_account, pause_job_for_doc, trigger_job_for_doc, change_release_date, and update_cost_center functions across erpnext/accounts/doctype/account/account.py, erpnext/accounts/doctype/process_payment_reconciliation/process_payment_reconciliation.py, erpnext/accounts/doctype/purchase_invoice/purchase_invoice.py, and erpnext/accounts/utils.py omit required write permission checks, allowing authenticated limited users to modify protected data beyond their roles. This issue is fixed in versions 15.112.0 and 16.22.0.

## References
- https://github.com/frappe/erpnext/releases/tag/v15.112.0
- https://github.com/frappe/erpnext/releases/tag/v16.22.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72910.json
- https://github.com/frappe/erpnext/security/advisories/GHSA-qpvh-75wh-j645
- https://nvd.nist.gov/vuln/detail/CVE-2026-72910
- https://github.com/frappe/erpnext/commit/2ae6451f10926bd12b6ce6c7dc40f08da83f2460
- https://github.com/frappe/erpnext/commit/8c7a313a38dfe38c9e35ca41e91389bcfaed2404
- https://github.com/frappe/erpnext/commit/ba936eefabb784805daa4c602b4baec9fc243ff8
- https://github.com/frappe/erpnext/pull/55709
