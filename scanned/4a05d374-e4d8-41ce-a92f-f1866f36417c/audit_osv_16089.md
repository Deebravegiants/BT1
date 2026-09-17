# [M] CVE-2019-25699

## Summary
Severity: Medium
Advisory: CVE-2019-25699
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-04-12
Source: https://osv.dev/vulnerability/CVE-2019-25699
Type: osv

## Details
Newsbull Haber Script 1.0.0 contains multiple SQL injection vulnerabilities in the search parameter that allow authenticated attackers to extract database information through time-based, blind, and boolean-based injection techniques. Attackers can inject malicious SQL code through the search parameter in endpoints like /admin/comment/records, /admin/category/records, /admin/news/records, and /admin/menu/childs to manipulate database queries and retrieve sensitive data.

## References
- http://newsbull.org/
- https://www.vulncheck.com/advisories/newsbull-haber-script-authenticated-sql-injection-via-search-parameter
- https://github.com/gurkanuzunca/newsbull
- https://www.exploit-db.com/exploits/46266
