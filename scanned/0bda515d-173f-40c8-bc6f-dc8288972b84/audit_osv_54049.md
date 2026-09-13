# [M] CVE-2023-37453

## Summary
Severity: Medium
Advisory: CVE-2023-37453
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-06
Source: https://osv.dev/vulnerability/CVE-2023-37453
Type: osv

## Details
An issue was discovered in the USB subsystem in the Linux kernel through 6.4.2. There is an out-of-bounds and crash in read_descriptors in drivers/usb/core/sysfs.c.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=de28e469da75359a2bb8cd8778b78aa64b1be1f4
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=ff33299ec8bb80cdcc073ad9c506bd79bb2ed20b
- https://lore.kernel.org/all/000000000000c0ffe505fe86c9ca%40google.com/T/
- https://lore.kernel.org/all/000000000000e56434059580f86e%40google.com/T/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=1e4c574225cc5a0553115e5eb5787d1474db5b0f
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=85d07c55621676d47d873d2749b88f783cd4d5a1
- https://syzkaller.appspot.com/bug?extid=18996170f8096c6174d0
