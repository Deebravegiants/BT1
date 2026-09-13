# [M] CVE-2025-27231

## Summary
Severity: Medium
Advisory: CVE-2025-27231
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-10-03
Source: https://osv.dev/vulnerability/CVE-2025-27231
Type: osv

## Details
The LDAP 'Bind password' value cannot be read after saving, but a Super Admin account can leak it by changing LDAP 'Host' to a rogue LDAP server. To mitigate this, the 'Bind password' value is now reset on 'Host' change.

## References
- https://support.zabbix.com/browse/ZBX-27062
