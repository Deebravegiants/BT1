# [C] SQL Injection in ChurchCRM EN_tyid Parameter via EditEventAttendees.php

## Summary
Severity: Critical
Advisory: CVE-2025-1132
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:L/SA:H/AU:Y/R:U/V:C/RE:H/U:Red)
Published: 2025-02-19
Source: https://osv.dev/vulnerability/CVE-2025-1132
Type: osv

## Details
A time-based blind SQL Injection vulnerability exists in the ChurchCRM 5.13.0 and prior EditEventAttendees.php within the EN_tyid parameter. The parameter is directly inserted into an SQL query without proper sanitization, allowing attackers to inject malicious SQL commands. Please note that the vulnerability requires Administrator permissions. This flaw can potentially allow attackers to delay the response, indicating the presence of an SQL injection vulnerability. While it is a time-based blind injection, it can be exploited to gain insights into the underlying database, and with further exploitation, sensitive data could be retrieved.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1132.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-1132
- https://github.com/ChurchCRM/CRM/issues/7251
