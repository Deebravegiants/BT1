# [H] CVE-2019-25703

## Summary
Severity: High
Advisory: CVE-2019-25703
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-12
Source: https://osv.dev/vulnerability/CVE-2019-25703
Type: osv

## Details
ImpressCMS 1.3.11 contains a time-based blind SQL injection vulnerability that allows authenticated attackers to manipulate database queries by injecting SQL code through the 'bid' parameter. Attackers can send POST requests to the admin.php endpoint with malicious 'bid' values containing SQL commands to extract sensitive database information.

## References
- http://www.impresscms.org/
- https://sourceforge.net/projects/impresscms/files/v1.3.11/impresscms_1.3.11.zip
- https://www.vulncheck.com/advisories/impresscms-sql-injection-via-bid-parameter
- https://www.exploit-db.com/exploits/46239
