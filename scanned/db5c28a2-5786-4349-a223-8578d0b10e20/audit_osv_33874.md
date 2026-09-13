# [M] CVE-2025-52043

## Summary
Severity: Medium
Advisory: CVE-2025-52043
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-09-30
Source: https://osv.dev/vulnerability/CVE-2025-52043
Type: osv

## Details
In Frappe ERPNext v15.57.5, the function import_coa() at erpnext/accounts/doctype/chart_of_accounts_importer/chart_of_accounts_importer.py is vulnerable to SQL injection, which allows an attacker to extract all information from databases by injecting a SQL query into the company parameter.

## References
- https://github.com/Vietsunshine-Electronic-Solution-JSC/Vulnerability-Disclosures/blob/main/2025/Frappe%20Framework%20-%20Multiple%20SQL%20Injection.md
- https://github.com/frappe/erpnext/pull/49192/commits/7fa4ed6139dfb737995fe297e40f4f5440c748c3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52043.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-52043
