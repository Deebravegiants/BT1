# [H] Crater - Cross-Company IDOR on Notes via Missing Company-Ownership Check in NotePolicy

## Summary
Severity: High
Advisory: CVE-2026-71242
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71242
Type: osv

## Details
Crater's NotePolicy checks only a blanket Bouncer ability (manage-all-notes / view-all-notes) with no company-ownership comparison, unlike InvoicePolicy and other sibling policies which additionally verify ->hasCompany(->company_id). Any authenticated user of one company can read, edit, or delete another company's notes by ID.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71242.json
- https://github.com/crater-invoice/crater
- https://nvd.nist.gov/vuln/detail/CVE-2026-71242
