# [M] CVE-2022-41849

## Summary
Severity: Medium
Advisory: CVE-2022-41849
CVSS: 4.2 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-30
Source: https://osv.dev/vulnerability/CVE-2022-41849
Type: osv

## Details
drivers/video/fbdev/smscufx.c in the Linux kernel through 5.19.12 has a race condition and resultant use-after-free if a physically proximate attacker removes a USB device while calling open(), aka a race condition between ufx_ops_open and ufx_usb_disconnect.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=5610bcfe8693c02e2e4c8b31427f1bdbdecc839c
- https://lore.kernel.org/all/20220925133243.GA383897%40ubuntu/T/
- https://lists.debian.org/debian-lts-announce/2022/12/msg00031.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00034.html
