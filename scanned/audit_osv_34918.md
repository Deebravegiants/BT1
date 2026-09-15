# [C] CVE-2025-66439

## Summary
Severity: Critical
Advisory: CVE-2025-66439
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-15
Source: https://osv.dev/vulnerability/CVE-2025-66439
Type: osv

## Details
An issue was discovered in Frappe ERPNext through 15.89.0. Function get_outstanding_reference_documents() at erpnext.accounts.doctype.payment_entry.payment_entry.py is vulnerable to SQL Injection. It allows an attacker to extract arbitrary data from the database by injecting SQL payloads via the from_posting_date parameter, which is directly interpolated into the query without proper sanitization or parameter binding.

## References
- https://github.com/frappe/frappe/security
- https://iamanc.github.io/post/erpnext-sqli
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66439.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-66439
