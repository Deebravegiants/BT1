# [M] CVE-2021-47811

## Summary
Severity: Medium
Advisory: CVE-2021-47811
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-01-16
Source: https://osv.dev/vulnerability/CVE-2021-47811
Type: osv

## Details
Grocery Crud 1.6.4 contains a SQL injection vulnerability in the order_by parameter that allows remote attackers to manipulate database queries. Attackers can inject malicious SQL code through the order_by[] parameter in POST requests to the ajax_list endpoint to potentially extract or modify database information.

## References
- https://www.grocerycrud.com/
- https://www.grocerycrud.com/downloads
- https://www.vulncheck.com/advisories/grocery-crud-orderby-sql-injection
- https://www.exploit-db.com/exploits/49985
