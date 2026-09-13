# [H] ax25: Remove broken autobind

## Summary
Severity: High
Advisory: CVE-2025-22109
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22109
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ax25: Remove broken autobind

Binding AX25 socket by using the autobind feature leads to memory leaks
in ax25_connect() and also refcount leaks in ax25_release(). Memory
leak was detected with kmemleak:

================================================================
unreferenced object 0xffff8880253cd680 (size 96):
backtrace:
__kmalloc_node_track_caller_noprof (./include/linux/kmemleak.h:43)
kmemdup_noprof (mm/util.c:136)
ax25_rt_autobind (net/ax25/ax25_route.c:428)
ax25_connect (net/ax25/af_ax25.c:1282)
__sys_connect_file (net/socket.c:2045)
__sys_connect (net/socket.c:2064)
__x64_sys_connect (net/socket.c:2067)
do_syscall_64 (arch/x86/entry/common.c:52 arch/x86/entry/common.c:83)
entry_SYSCALL_64_after_hwframe (arch/x86/entry/entry_64.S:130)
================================================================

When socket is bound, refcounts must be incremented the way it is done
in ax25_bind() and ax25_setsockopt() (SO_BINDTODEVICE). In case of
autobind, the refcounts are not incremented.

This bug leads to the following issue reported by Syzkaller:

================================================================
ax25_connect(): syz-executor318 uses autobind, please contact jreuter@yaina.de
------------[ cut here ]------------
refcount_t: decrement hit 0; leaking memory.
WARNING: CPU: 0 PID: 5317 at lib/refcount.c:31 refcount_warn_saturate+0xfa/0x1d0 lib/refcount.c:31
Modules linked in:
CPU: 0 UID: 0 PID: 5317 Comm: syz-executor318 Not tainted 6.14.0-rc4-syzkaller-00278-gece144f151ac #0
Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 1.16.3-debian-1.16.3-2~bpo12+1 04/01/2014
RIP: 0010:refcount_warn_saturate+0xfa/0x1d0 lib/refcount.c:31
...
Call Trace:
 <TASK>
 __refcount_dec include/linux/refcount.h:336 [inline]
 refcount_dec include/linux/refcount.h:351 [inline]
 ref_tracker_free+0x6af/0x7e0 lib/ref_tracker.c:236
 netdev_tracker_free include/linux/netdevice.h:4302 [inline]
 netdev_put include/linux/netdevice.h:4319 [inline]
 ax25_release+0x368/0x960 net/ax25/af_ax25.c:1080
 __sock_release net/socket.c:647 [inline]
 sock_close+0xbc/0x240 net/socket.c:1398
 __fput+0x3e9/0x9f0 fs/file_table.c:464
 __do_sys_close fs/open.c:1580 [inline]
 __se_sys_close fs/open.c:1565 [inline]
 __x64_sys_close+0x7f/0x110 fs/open.c:1565
 do_syscall_x64 arch/x86/entry/common.c:52 [inline]
 do_syscall_64+0xf3/0x230 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x77/0x7f
 ...
 </TASK>
================================================================

Considering the issues above and the comments left in the code that say:
"check if we can remove this feature. It is broken."; "autobinding in this
may or may not work"; - it is better to completely remove this feature than
to fix it because it is broken and leads to various kinds of memory bugs.

Now calling connect() without first binding socket will result in an
error (-EINVAL). Userspace software that relies on the autobind feature
might get broken. However, this feature does not seem widely used with
this specific driver as it was not reliable at any point of time, and it
is already broken anyway. E.g. ax25-tools and ax25-apps packages for
popular distributions do not use the autobind feature for AF_AX25.

Found by Linux Verification Center (linuxtesting.org) with Syzkaller.

## References
- https://git.kernel.org/stable/c/2f6efbabceb6b2914ee9bafb86d9a51feae9cce8
- https://git.kernel.org/stable/c/61203fdd3e35519db9a98b6ff8983c620ffc4696
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22109.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22109
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
