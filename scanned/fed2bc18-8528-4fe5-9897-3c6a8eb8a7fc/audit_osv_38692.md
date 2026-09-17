# [C] Krayin CRM < 2.2.4 Blind SQL Injection via LeadDataGrid.php rotten_lead Parameter

## Summary
Severity: Critical
Advisory: CVE-2026-41453
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-41453
Type: osv

## Details
Krayin CRM before 2.2.4 contains a blind SQL injection vulnerability in the leads DataGrid that allows authenticated users with leads access to inject arbitrary SQL into a HAVING clause by manipulating the rotten_lead[in] query parameter, which is concatenated without parameterized binding directly into a havingRaw() call in LeadDataGrid.php. Attackers can exploit this flaw using time-based and boolean-based blind injection techniques to extract the entire database contents, including user credential hashes, CRM records, and application configuration data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41453.json
- https://github.com/krayin/laravel-crm/releases/tag/v2.2.4
- https://nvd.nist.gov/vuln/detail/CVE-2026-41453
- https://www.vulncheck.com/advisories/krayin-crm-blind-sql-injection-via-leaddatagrid-php-rotten-lead-parameter
- https://github.com/krayin/laravel-crm/commit/2a3724cb7e9e65ab98f2b42c8ca2c98dede48f62
- https://github.com/krayin/laravel-crm
- https://jivasecurity.com/writeups/krayin-lead-datagrid-sqli-cve-2026-41453
