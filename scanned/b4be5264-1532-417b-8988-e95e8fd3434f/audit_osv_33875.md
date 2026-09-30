# [H] CVE-2025-52044

## Summary
Severity: High
Advisory: CVE-2025-52044
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-52044
Type: osv

## Details
In Frappe ERPNext v15.57.5, the function get_stock_balance() at erpnext/stock/utils.py is vulnerable to SQL Injection, which allows an attacker to extract all information from databases by injecting SQL query into inventory_dimensions_dict parameter.

## References
- https://github.com/Vietsunshine-Electronic-Solution-JSC/Vulnerability-Disclosures/blob/main/2025/Frappe%20Framework%20-%20Multiple%20SQL%20Injection.md
- https://github.com/frappe/erpnext/pull/49192/commits/eb22794f14351c2ff5731548c48bef0b91765c86
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52044.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-52044
