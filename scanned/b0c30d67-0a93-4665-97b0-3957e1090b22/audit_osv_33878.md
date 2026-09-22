# [M] CVE-2025-52049

## Summary
Severity: Medium
Advisory: CVE-2025-52049
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-09-30
Source: https://osv.dev/vulnerability/CVE-2025-52049
Type: osv

## Details
In Frappe ErpNext v15.57.5, the function get_timesheet_detail_rate() at erpnext/projects/doctype/timesheet/timesheet.py is vulnerable to SQL Injection, which allows an attacker to extract all information from databases by injecting SQL query into the timelog parameter.

## References
- https://github.com/Vietsunshine-Electronic-Solution-JSC/Vulnerability-Disclosures/blob/main/2025/Frappe%20Framework%20-%20Multiple%20SQL%20Injection.md
- https://github.com/frappe/erpnext/pull/49192/commits/e563ed0c75fd20135a6ad288e957e75eac7d3b8d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52049.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-52049
