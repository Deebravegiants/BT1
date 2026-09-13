# [M] CVE-2021-47641

## Summary
Severity: Medium
Advisory: CVE-2021-47641
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2021-47641
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

video: fbdev: cirrusfb: check pixclock to avoid divide by zero

Do a sanity check on pixclock value to avoid divide by zero.

If the pixclock value is zero, the cirrusfb driver will round up
pixclock to get the derived frequency as close to maxclock as
possible.

Syzkaller reported a divide error in cirrusfb_check_pixclock.

divide error: 0000 [#1] SMP KASAN PTI
CPU: 0 PID: 14938 Comm: cirrusfb_test Not tainted 5.15.0-rc6 #1
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.11.0-2
RIP: 0010:cirrusfb_check_var+0x6f1/0x1260

Call Trace:
 fb_set_var+0x398/0xf90
 do_fb_ioctl+0x4b8/0x6f0
 fb_ioctl+0xeb/0x130
 __x64_sys_ioctl+0x19d/0x220
 do_syscall_64+0x3a/0x80
 entry_SYSCALL_64_after_hwframe+0x44/0xae

## References
- https://git.kernel.org/stable/c/1d3fb46439ad4e8f0c5739eb33d1875ac9e0f135
- https://git.kernel.org/stable/c/40b13e3d85744210db13457785646634e2d056bd
- https://git.kernel.org/stable/c/53a2088a396cfa1da92690a1da289634cd73bf0d
- https://git.kernel.org/stable/c/e498b504f8c81b07efab9febf8503448de4dc9cf
- https://git.kernel.org/stable/c/45800c42ef000f417270bcfc08630e42486fca99
- https://git.kernel.org/stable/c/5c6f402bdcf9e7239c6bc7087eda71ac99b31379
- https://git.kernel.org/stable/c/6fe23ff94e7840097202e85c148688940b37c9b1
- https://git.kernel.org/stable/c/8c7e2141fb89c620ab4e41512e262fbf25b8260d
- https://git.kernel.org/stable/c/c656d04247a2654ede5cead2ecbf83431dad5261
