# [H] CVE-2019-25663

## Summary
Severity: High
Advisory: CVE-2019-25663
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-04-05
Source: https://osv.dev/vulnerability/CVE-2019-25663
Type: osv

## Details
SuiteCRM 7.10.7 contains a SQL injection vulnerability that allows authenticated attackers to manipulate database queries by injecting SQL code through the parentTab parameter. Attackers can send GET requests to the email module with malicious parentTab values using boolean-based SQL injection techniques to extract sensitive database information.

## References
- https://suitecrm.com/
- https://suitecrm.com/download/
- https://www.vulncheck.com/advisories/suitecrm-sql-injection-via-parenttab-parameter
- https://www.exploit-db.com/exploits/46310
