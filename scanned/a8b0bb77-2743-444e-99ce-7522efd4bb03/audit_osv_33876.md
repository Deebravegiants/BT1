# [M] CVE-2025-52047

## Summary
Severity: Medium
Advisory: CVE-2025-52047
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-09-30
Source: https://osv.dev/vulnerability/CVE-2025-52047
Type: osv

## Details
In Frappe ErpNext v15.57.5, the function get_income_account() at erpnext/controllers/queries.py is vulnerable to SQL Injection, which allows an attacker to extract all information from databases by injecting a SQL query into the filters.disabled parameter.

## References
- https://github.com/Vietsunshine-Electronic-Solution-JSC/Vulnerability-Disclosures/blob/main/2025/Frappe%20Framework%20-%20Multiple%20SQL%20Injection.md
- https://github.com/frappe/erpnext/pull/49192/commits/6320f7290f93a5278ffdfaa790af70427c20a1c8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52047.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-52047
