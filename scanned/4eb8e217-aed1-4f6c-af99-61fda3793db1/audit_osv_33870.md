# [H] CVE-2025-52039

## Summary
Severity: High
Advisory: CVE-2025-52039
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-52039
Type: osv

## Details
In Frappe ERPNext 15.57.5, the function get_material_requests_based_on_supplier() at erpnext/stock/doctype/material_request/material_request.py is vulnerable to SQL Injection, which allows an attacker to extract all information from databases by injecting a SQL query into the txt parameter.

## References
- https://github.com/Vietsunshine-Electronic-Solution-JSC/Vulnerability-Disclosures/blob/main/2025/Frappe%20Framework%20-%20Multiple%20SQL%20Injection.md
- https://github.com/frappe/erpnext/pull/49192/commits/de919568b4f7a86c8d418c0c3fd88e1f3101696c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52039.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-52039
