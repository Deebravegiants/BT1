# [M] CVE-2022-43750

## Summary
Severity: Medium
Advisory: CVE-2022-43750
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-26
Source: https://osv.dev/vulnerability/CVE-2022-43750
Type: osv

## Details
drivers/usb/mon/mon_bin.c in usbmon in the Linux kernel before 5.19.15 and 6.x before 6.0.1 allows a user-space client to corrupt the monitor's internal memory.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.0.1
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00034.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.15
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=a659daf63d16aa883be42f3f34ff84235c302198
- https://github.com/torvalds/linux/commit/a659daf63d16aa883be42f3f34ff84235c302198
