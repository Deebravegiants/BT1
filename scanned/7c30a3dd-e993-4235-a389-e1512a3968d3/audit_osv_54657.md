# [M] CVE-2024-24861

## Summary
Severity: Medium
Advisory: CVE-2024-24861
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-02-05
Source: https://osv.dev/vulnerability/CVE-2024-24861
Type: osv

## Details
A race condition was found in the Linux kernel's media/xc4000 device driver in xc4000 xc4000_get_frequency() function. This can result in return value overflow issue, possibly leading to malfunction or denial of service issue.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://bugzilla.openanolis.cn/show_bug.cgi?id=8150
