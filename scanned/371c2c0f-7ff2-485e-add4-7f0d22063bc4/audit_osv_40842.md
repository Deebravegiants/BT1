# [H] Crater - Missing Tenant-Ownership Check in CustomerPolicy Allows Cross-Company Customer Data Theft and Deletion

## Summary
Severity: High
Advisory: CVE-2026-55739
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-55739
Type: osv

## Details
Crater isolates data per company_id, and its Invoice/Estimate/Payment/Expense policies enforce both a Bouncer ability check and ->hasCompany(->company_id). CustomerPolicy's view/update/delete methods omit the company-ownership check entirely, checking only the blanket ability. Route-model-bound customer lookups and the bulk Customer::deleteCustomers method are similarly unscoped (self::find with no company filter).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55739.json
- https://github.com/crater-invoice/crater
- https://nvd.nist.gov/vuln/detail/CVE-2026-55739
