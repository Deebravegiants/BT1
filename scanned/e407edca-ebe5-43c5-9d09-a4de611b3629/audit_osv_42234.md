# [H] ERPNext: SQL Injection in "Inactive Customers" report via unvalidated `doctype` filter

## Summary
Severity: High
Advisory: CVE-2026-65822
Aliases: GHSA-x35x-4mvx-h959
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-65822
Type: osv

## Details
ERPNext is a free and open source Enterprise Resource Planning tool. Prior to 15.116.0 and 16.23.0, erpnext/selling/report/inactive_customers/inactive_customers.py accepts an unvalidated doctype filter and interpolates it into raw SQL in get_sales_details and get_last_sales_amt, allowing an authenticated user to extract sensitive information and manipulate database queries. This issue is fixed in versions 15.116.0 and 16.23.0.

## References
- https://github.com/frappe/erpnext/releases/tag/v15.116.0
- https://github.com/frappe/erpnext/releases/tag/v16.23.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65822.json
- https://github.com/frappe/erpnext/security/advisories/GHSA-x35x-4mvx-h959
- https://nvd.nist.gov/vuln/detail/CVE-2026-65822
- https://github.com/frappe/erpnext/commit/29dd6e6681d20bbacb69517d2d2c875aa929eb9e
- https://github.com/frappe/erpnext/commit/f43af6624610e874e61ad3faf8701e5e6be6271a
- https://github.com/frappe/erpnext/pull/55721
