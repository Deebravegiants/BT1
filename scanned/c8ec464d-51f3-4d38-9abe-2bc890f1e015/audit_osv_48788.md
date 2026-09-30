# [H] CVE-2018-13406

## Summary
Severity: High
Advisory: CVE-2018-13406
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-06
Source: https://osv.dev/vulnerability/CVE-2018-13406
Type: osv

## Details
An integer overflow in the uvesafb_setcmap function in drivers/video/fbdev/uvesafb.c in the Linux kernel before 4.17.4 could result in local attackers being able to crash the kernel or potentially elevate privileges because kmalloc_array is not used.

## References
- http://www.securityfocus.com/bid/104685
- https://usn.ubuntu.com/3752-2/
- https://usn.ubuntu.com/3752-3/
- https://usn.ubuntu.com/3753-1/
- https://usn.ubuntu.com/3753-2/
- http://www.securitytracker.com/id/1041355
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.17.4
- https://lists.debian.org/debian-lts-announce/2019/03/msg00017.html
- https://usn.ubuntu.com/3752-1/
- https://usn.ubuntu.com/3754-1/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=9f645bcc566a1e9f921bdae7528a01ced5bc3713
- https://github.com/torvalds/linux/commit/9f645bcc566a1e9f921bdae7528a01ced5bc3713
