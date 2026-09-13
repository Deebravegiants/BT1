# [M] CVE-2022-45888

## Summary
Severity: Medium
Advisory: CVE-2022-45888
CVSS: 6.4 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-25
Source: https://osv.dev/vulnerability/CVE-2022-45888
Type: osv

## Details
An issue was discovered in the Linux kernel through 6.0.9. drivers/char/xillybus/xillyusb.c has a race condition and use-after-free during physical removal of a USB device.

## References
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=282a4b71816b6076029017a7bab3a9dcee12a920
- https://lore.kernel.org/all/20221022175404.GA375335%40ubuntu/
- https://security.netapp.com/advisory/ntap-20230113-0006/
