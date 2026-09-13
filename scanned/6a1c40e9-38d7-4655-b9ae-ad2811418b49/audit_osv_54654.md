# [M] CVE-2024-24858

## Summary
Severity: Medium
Advisory: CVE-2024-24858
CVSS: 5.3 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-05
Source: https://osv.dev/vulnerability/CVE-2024-24858
Type: osv

## Details
A race condition was found in the Linux kernel's net/bluetooth in {conn,adv}_{min,max}_interval_set() function. This can result in I2cap connection or broadcast abnormality issue, possibly leading to denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://bugzilla.openanolis.cn/show_bug.cgi?id=8154
