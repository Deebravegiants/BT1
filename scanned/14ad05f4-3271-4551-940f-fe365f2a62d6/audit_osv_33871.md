# [H] CVE-2025-52040

## Summary
Severity: High
Advisory: CVE-2025-52040
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-52040
Type: osv

## Details
In Frappe ERPNext 15.57.5, the function get_blanket_orders() at erpnext/controllers/queries.py is vulnerable to SQL Injection, which allows an attacker can extract all information from databases by injecting a SQL query into the blanket_order_type parameter.

## References
- https://github.com/Vietsunshine-Electronic-Solution-JSC/Vulnerability-Disclosures/blob/main/2025/Frappe%20Framework%20-%20Multiple%20SQL%20Injection.md
- https://github.com/frappe/erpnext/pull/49192/commits/1db135262d9474411ef54e3367d24bb169d2503e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52040.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-52040
