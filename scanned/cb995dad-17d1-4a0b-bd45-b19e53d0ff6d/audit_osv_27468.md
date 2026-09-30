# [H] CVE-2024-22116

## Summary
Severity: High
Advisory: CVE-2024-22116
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-12
Source: https://osv.dev/vulnerability/CVE-2024-22116
Type: osv

## Details
An administrator with restricted permissions can exploit the script execution functionality within the Monitoring Hosts section. The lack of default escaping for script parameters enabled this user ability to execute arbitrary code via the Ping script, thereby compromising infrastructure.

## References
- https://lists.debian.org/debian-lts-announce/2024/10/msg00000.html
- https://support.zabbix.com/browse/ZBX-25016
