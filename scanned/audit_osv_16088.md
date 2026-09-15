# [H] CVE-2019-25684

## Summary
Severity: High
Advisory: CVE-2019-25684
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-04-05
Source: https://osv.dev/vulnerability/CVE-2019-25684
Type: osv

## Details
OpenDocMan 1.3.4 contains an SQL injection vulnerability that allows unauthenticated attackers to manipulate database queries by injecting SQL code through the 'where' parameter. Attackers can send GET requests to search.php with malicious SQL payloads in the 'where' parameter to extract sensitive database information.

## References
- https://sourceforge.net/projects/opendocman/files/
- https://www.vulncheck.com/advisories/opendocman-sql-injection-via-where-parameter
- https://www.exploit-db.com/exploits/46500
