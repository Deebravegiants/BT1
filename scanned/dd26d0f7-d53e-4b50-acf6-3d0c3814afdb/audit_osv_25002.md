# [M] CVE-2023-29449

## Summary
Severity: Medium
Advisory: CVE-2023-29449
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-13
Source: https://osv.dev/vulnerability/CVE-2023-29449
Type: osv

## Details
JavaScript preprocessing, webhooks and global scripts can cause uncontrolled CPU, memory, and disk I/O utilization. Preprocessing/webhook/global script configuration and testing are only available to Administrative roles (Admin and Superadmin). Administrative privileges should be typically granted to users who need to perform tasks that require more control over the system. The security risk is limited because not all users have this level of access.

## References
- https://lists.debian.org/debian-lts-announce/2024/10/msg00000.html
- https://support.zabbix.com/browse/ZBX-22589
