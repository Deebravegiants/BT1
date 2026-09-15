# [H] CVE-2024-36465

## Summary
Severity: High
Advisory: CVE-2024-36465
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-02
Source: https://osv.dev/vulnerability/CVE-2024-36465
Type: osv

## Details
A low privilege (regular) Zabbix user with API access can use SQL injection vulnerability in include/classes/api/CApiService.php to execute arbitrary SQL commands via the groupBy parameter.

## References
- https://support.zabbix.com/browse/ZBX-26257
