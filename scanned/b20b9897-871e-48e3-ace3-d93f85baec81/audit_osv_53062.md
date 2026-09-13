# [M] CVE-2022-26966

## Summary
Severity: Medium
Advisory: CVE-2022-26966
Aliases: A-225469258, PUB-A-225469258
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-03-12
Source: https://osv.dev/vulnerability/CVE-2022-26966
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.16.12. drivers/net/usb/sr9700.c allows attackers to obtain sensitive information from heap memory via crafted frame lengths from a device.

## References
- https://lists.debian.org/debian-lts-announce/2022/07/msg00000.html
- https://security.netapp.com/advisory/ntap-20220419-0001/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.10
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=e9da0b56fe27206b49f39805f7dcda8a89379062
