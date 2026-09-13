# [C] SQL Injection in ChurchCRM CurrentFundraiser Parameter via DonatedItemEditor.php

## Summary
Severity: Critical
Advisory: CVE-2025-1134
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:L/SA:H/AU:Y/R:U/V:C/RE:H/U:Red)
Published: 2025-02-19
Source: https://osv.dev/vulnerability/CVE-2025-1134
Type: osv

## Details
A vulnerability exists in ChurchCRM 5.13.0 and prior that allows an attacker to execute arbitrary SQL queries by exploiting a boolean-based and time-based blind SQL Injection vulnerability in the DonatedItemEditor functionality. The CurrentFundraiser parameter is directly concatenated into an SQL query without sufficient sanitization, allowing an attacker to manipulate database queries and execute arbitrary commands, potentially leading to data exfiltration, modification, or deletion. Please note that this vulnerability requires Administrator privileges.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1134.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-1134
- https://github.com/ChurchCRM/CRM/issues/7253
