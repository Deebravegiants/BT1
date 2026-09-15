# [H] CVE-2019-25664

## Summary
Severity: High
Advisory: CVE-2019-25664
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-04-05
Source: https://osv.dev/vulnerability/CVE-2019-25664
Type: osv

## Details
SuiteCRM 7.10.7 contains a time-based SQL injection vulnerability in the record parameter of the Users module DetailView action that allows authenticated attackers to manipulate database queries. Attackers can append SQL code to the record parameter in GET requests to the index.php endpoint to extract sensitive database information through time-based blind SQL injection techniques.

## References
- https://suitecrm.com/
- https://suitecrm.com/download/
- https://www.vulncheck.com/advisories/suitecrm-sql-injection-via-record-parameter
- https://www.exploit-db.com/exploits/46311
