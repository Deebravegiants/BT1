# [H] FrontAccounting < 2.4.20 SQL Injection via get_gl_transactions()

## Summary
Severity: High
Advisory: CVE-2026-40524
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-40524
Type: osv

## Details
FrontAccounting before 2.4.20 contains a SQL injection vulnerability in the get_gl_transactions() function where the filter_type parameter is concatenated directly into a SQL IN() clause without parameterization. Attackers with SA_GLANALYTIC permission can inject arbitrary SQL by supplying a closing parenthesis followed by malicious conditions to extract sensitive journal entry data through boolean-based blind SQL injection with reliable response size differentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40524.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40524
- https://sourceforge.net/p/frontaccounting/news/2026/04/release-2420/
- https://www.vulncheck.com/advisories/frontaccounting-sql-injection-via-get-gl-transactions
- https://github.com/FrontAccountingERP/FA/commit/647a18196caad27f96ea852e993c9e30f815357f
- https://jivasecurity.com/writeups/frontaccounting-sqli-journal-entries-report-cve-2026-40524
