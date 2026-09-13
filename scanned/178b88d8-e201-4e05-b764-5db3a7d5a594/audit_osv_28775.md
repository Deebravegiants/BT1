# [H] CVE-2024-36468

## Summary
Severity: High
Advisory: CVE-2024-36468
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2024-11-27
Source: https://osv.dev/vulnerability/CVE-2024-36468
Type: osv

## Details
The reported vulnerability is a stack buffer overflow in the zbx_snmp_cache_handle_engineid function within the Zabbix server/proxy code. This issue occurs when copying data from session->securityEngineID to local_record.engineid without proper bounds checking.

## References
- https://support.zabbix.com/browse/ZBX-25621
