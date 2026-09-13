# [C] CVE-2022-43515

## Summary
Severity: Critical
Advisory: CVE-2022-43515
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-05
Source: https://osv.dev/vulnerability/CVE-2022-43515
Type: osv

## Details
Zabbix Frontend provides a feature that allows admins to maintain the installation and ensure that only certain IP addresses can access it. In this way, any user will not be able to access the Zabbix Frontend while it is being maintained and possible sensitive data will be prevented from being disclosed. An attacker can bypass this protection and access the instance using IP address not listed in the defined range.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00027.html
- https://lists.debian.org/debian-lts-announce/2024/10/msg00000.html
- https://support.zabbix.com/browse/ZBX-22050
