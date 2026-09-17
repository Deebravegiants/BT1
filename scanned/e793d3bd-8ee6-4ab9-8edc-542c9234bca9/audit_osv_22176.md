# [H] CVE-2022-23132

## Summary
Severity: High
Advisory: CVE-2022-23132
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-01-13
Source: https://osv.dev/vulnerability/CVE-2022-23132
Type: osv

## Details
During Zabbix installation from RPM, DAC_OVERRIDE SELinux capability is in use to access PID files in [/var/run/zabbix] folder. In this case, Zabbix Proxy or Server processes can bypass file read, write and execute permissions check on the file system level

## References
- https://lists.debian.org/debian-lts-announce/2024/10/msg00000.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6SZYHXINBKCY42ITFSNCYE7KCSF33VRA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VB6W556GVXOKUYTASTDGL3AI7S3SJHX7/
- https://support.zabbix.com/browse/ZBX-20341
