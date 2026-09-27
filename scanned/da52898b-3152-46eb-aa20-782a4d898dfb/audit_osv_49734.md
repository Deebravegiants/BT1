# [C] CVE-2019-17382

## Summary
Severity: Critical
Advisory: CVE-2019-17382
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2019-10-09
Source: https://osv.dev/vulnerability/CVE-2019-17382
Type: osv

## Details
An issue was discovered in zabbix.php?action=dashboard.view&dashboardid=1 in Zabbix through 4.4. An attacker can bypass the login page and access the dashboard page, and then create a Dashboard, Report, Screen, or Map without any Username/Password (i.e., anonymously). All created elements (Dashboard/Report/Screen/Map) are accessible by other users and by an admin.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00027.html
- https://www.exploit-db.com/exploits/47467
