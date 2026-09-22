# [M] CVE-2024-24857

## Summary
Severity: Medium
Advisory: CVE-2024-24857
CVSS: 6.8 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-02-05
Source: https://osv.dev/vulnerability/CVE-2024-24857
Type: osv

## Details
A race condition was found in the Linux kernel's net/bluetooth device driver in conn_info_{min,max}_age_set() function. This can result in integrity overflow issue, possibly leading to bluetooth connection abnormality or denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://bugzilla.openanolis.cn/show_bug.cgi?id=8155
