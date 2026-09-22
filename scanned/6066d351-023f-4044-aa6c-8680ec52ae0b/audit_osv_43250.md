# [M] ERPNext: Unauthorised triggering of automated emails due to missing validation

## Summary
Severity: Medium
Advisory: CVE-2026-72906
Aliases: GHSA-3x6c-gc4v-f5v8
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72906
Type: osv

## Details
ERPNext is a free and open source Enterprise Resource Planning tool. Prior to 15.111.0 and 16.22.0, the send_auto_email function in erpnext/accounts/doctype/process_statement_of_accounts/process_statement_of_accounts.py lacks a Process Statement Of Accounts permission check, allowing an authenticated low-privilege user to trigger automated emails outside the permitted role. This issue is fixed in versions 15.111.0 and 16.22.0.

## References
- https://github.com/frappe/erpnext/releases/tag/v15.111.0
- https://github.com/frappe/erpnext/releases/tag/v16.22.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72906.json
- https://github.com/frappe/erpnext/security/advisories/GHSA-3x6c-gc4v-f5v8
- https://nvd.nist.gov/vuln/detail/CVE-2026-72906
- https://github.com/frappe/erpnext/commit/18ca96c36ba65362bf1c25abb8eab32c64c6c7dd
- https://github.com/frappe/erpnext/commit/e15879acd118ccd343e31ad3b5a6279e514c82c2
- https://github.com/frappe/erpnext/pull/55781
