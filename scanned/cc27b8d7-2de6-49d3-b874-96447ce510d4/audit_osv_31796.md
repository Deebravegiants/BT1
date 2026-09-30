# [H] ax25: Fix refcount leak caused by setting SO_BINDTODEVICE sockopt

## Summary
Severity: High
Advisory: CVE-2025-21792
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21792
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.129, >=6.2.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ax25: Fix refcount leak caused by setting SO_BINDTODEVICE sockopt

If an AX25 device is bound to a socket by setting the SO_BINDTODEVICE
socket option, a refcount leak will occur in ax25_release().

Commit 9fd75b66b8f6 ("ax25: Fix refcount leaks caused by ax25_cb_del()")
added decrement of device refcounts in ax25_release(). In order for that
to work correctly the refcounts must already be incremented when the
device is bound to the socket. An AX25 device can be bound to a socket
by either calling ax25_bind() or setting SO_BINDTODEVICE socket option.
In both cases the refcounts should be incremented, but in fact it is done
only in ax25_bind().

This bug leads to the following issue reported by Syzkaller:

================================================================
refcount_t: decrement hit 0; leaking memory.
WARNING: CPU: 1 PID: 5932 at lib/refcount.c:31 refcount_warn_saturate+0x1ed/0x210 lib/refcount.c:31
Modules linked in:
CPU: 1 UID: 0 PID: 5932 Comm: syz-executor424 Not tainted 6.13.0-rc4-syzkaller-00110-g4099a71718b0 #0
Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 1.16.3-debian-1.16.3-2~bpo12+1 04/01/2014
RIP: 0010:refcount_warn_saturate+0x1ed/0x210 lib/refcount.c:31
Call Trace:
 <TASK>
 __refcount_dec include/linux/refcount.h:336 [inline]
 refcount_dec include/linux/refcount.h:351 [inline]
 ref_tracker_free+0x710/0x820 lib/ref_tracker.c:236
 netdev_tracker_free include/linux/netdevice.h:4156 [inline]
 netdev_put include/linux/netdevice.h:4173 [inline]
 netdev_put include/linux/netdevice.h:4169 [inline]
 ax25_release+0x33f/0xa10 net/ax25/af_ax25.c:1069
 __sock_release+0xb0/0x270 net/socket.c:640
 sock_close+0x1c/0x30 net/socket.c:1408
 ...
 do_syscall_x64 arch/x86/entry/common.c:52 [inline]
 do_syscall_64+0xcd/0x250 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x77/0x7f
 ...
 </TASK>
================================================================

Fix the implementation of ax25_setsockopt() by adding increment of
refcounts for the new device bound, and decrement of refcounts for
the old unbound device.

## References
- https://git.kernel.org/stable/c/470bda72fda0fcf54300466d70ce2de62f7835d2
- https://git.kernel.org/stable/c/90056ece99966182dc0e367f3fd2afab46ada847
- https://git.kernel.org/stable/c/94a0de224ed52eb2ecd4f4cb1b937b674c9fb955
- https://git.kernel.org/stable/c/b58f7ca86a7b8e480c06e30c5163c5d2f4e24023
- https://git.kernel.org/stable/c/bca0902e61731a75fc4860c8720168d9f1bae3b6
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21792.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21792
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
