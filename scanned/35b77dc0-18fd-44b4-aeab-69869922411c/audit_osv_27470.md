# [H] CVE-2024-22120

## Summary
Severity: High
Advisory: CVE-2024-22120
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-22120
Type: osv

## Details
Zabbix server can perform command execution for configured scripts. After command is executed, audit entry is added to "Audit Log". Due to "clientip" field is not sanitized, it is possible to injection SQL into "clientip" and exploit time based blind SQL injection.

## References
- https://support.zabbix.com/browse/ZBX-24505
