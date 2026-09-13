# [C] SuiteCRM < 7.12.6 SQL Injection via 'export' Functionality

## Summary
Severity: Critical
Advisory: CVE-2022-50589
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-11-06
Source: https://osv.dev/vulnerability/CVE-2022-50589
Type: osv

## Details
SuiteCRM versions prior to 7.12.6 contain a SQL injection vulnerability within the processing of the ‘uid’ parameter within the ‘export’ functionality. Successful exploitation allows remote unauthenticated attackers to ultimately execute arbitrary code.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50589.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50589
- https://www.vulncheck.com/advisories/suitecrm-sqli-via-export-functionality
- https://docs.suitecrm.com/admin/releases/7.12.x/#_7_12_6
- https://github.com/SuiteCRM/SuiteCRM
- https://blog.exodusintel.com/2022/06/09/salesagility-suitecrm-export-request-sql-injection-vulnerability/
