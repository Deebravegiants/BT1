# [H] CVE-2019-11600

## Summary
Severity: High
Advisory: CVE-2019-11600
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-13
Source: https://osv.dev/vulnerability/CVE-2019-11600
Type: osv

## Details
A SQL injection vulnerability in the activities API in OpenProject before 8.3.2 allows a remote attacker to execute arbitrary SQL commands via the id parameter. The attack can be performed unauthenticated if OpenProject is configured not to require authentication for API access.

## References
- https://groups.google.com/forum/#%21msg/openproject-security/XlucAJMxmzM/hESpOaFVAwAJ
- https://www.openproject.org/release-notes/openproject-8-3-2/
- https://seclists.org/bugtraq/2019/May/22
- http://packetstormsecurity.com/files/152806/OpenProject-8.3.1-SQL-Injection.html
- http://seclists.org/fulldisclosure/2019/May/7
