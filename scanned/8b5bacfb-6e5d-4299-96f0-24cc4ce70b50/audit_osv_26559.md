# [M] can: bcm: bcm_tx_setup(): fix KMSAN uninit-value in vfs_write

## Summary
Severity: Medium
Advisory: CVE-2023-53344
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2023-53344
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <4.14.312, >=4.15.0 <4.19.280, >=4.20.0 <5.4.240, >=5.5.0 <5.10.177, >=5.11.0 <5.15.106, >=5.16.0 <6.1.23, >=6.2.0 <6.2.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: bcm: bcm_tx_setup(): fix KMSAN uninit-value in vfs_write

Syzkaller reported the following issue:

=====================================================
BUG: KMSAN: uninit-value in aio_rw_done fs/aio.c:1520 [inline]
BUG: KMSAN: uninit-value in aio_write+0x899/0x950 fs/aio.c:1600
 aio_rw_done fs/aio.c:1520 [inline]
 aio_write+0x899/0x950 fs/aio.c:1600
 io_submit_one+0x1d1c/0x3bf0 fs/aio.c:2019
 __do_sys_io_submit fs/aio.c:2078 [inline]
 __se_sys_io_submit+0x293/0x770 fs/aio.c:2048
 __x64_sys_io_submit+0x92/0xd0 fs/aio.c:2048
 do_syscall_x64 arch/x86/entry/common.c:50 [inline]
 do_syscall_64+0x3d/0xb0 arch/x86/entry/common.c:80
 entry_SYSCALL_64_after_hwframe+0x63/0xcd

Uninit was created at:
 slab_post_alloc_hook mm/slab.h:766 [inline]
 slab_alloc_node mm/slub.c:3452 [inline]
 __kmem_cache_alloc_node+0x71f/0xce0 mm/slub.c:3491
 __do_kmalloc_node mm/slab_common.c:967 [inline]
 __kmalloc+0x11d/0x3b0 mm/slab_common.c:981
 kmalloc_array include/linux/slab.h:636 [inline]
 bcm_tx_setup+0x80e/0x29d0 net/can/bcm.c:930
 bcm_sendmsg+0x3a2/0xce0 net/can/bcm.c:1351
 sock_sendmsg_nosec net/socket.c:714 [inline]
 sock_sendmsg net/socket.c:734 [inline]
 sock_write_iter+0x495/0x5e0 net/socket.c:1108
 call_write_iter include/linux/fs.h:2189 [inline]
 aio_write+0x63a/0x950 fs/aio.c:1600
 io_submit_one+0x1d1c/0x3bf0 fs/aio.c:2019
 __do_sys_io_submit fs/aio.c:2078 [inline]
 __se_sys_io_submit+0x293/0x770 fs/aio.c:2048
 __x64_sys_io_submit+0x92/0xd0 fs/aio.c:2048
 do_syscall_x64 arch/x86/entry/common.c:50 [inline]
 do_syscall_64+0x3d/0xb0 arch/x86/entry/common.c:80
 entry_SYSCALL_64_after_hwframe+0x63/0xcd

CPU: 1 PID: 5034 Comm: syz-executor350 Not tainted 6.2.0-rc6-syzkaller-80422-geda666ff2276 #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 01/12/2023
=====================================================

We can follow the call chain and find that 'bcm_tx_setup' function
calls 'memcpy_from_msg' to copy some content to the newly allocated
frame of 'op->frames'. After that the 'len' field of copied structure
being compared with some constant value (64 or 8). However, if
'memcpy_from_msg' returns an error, we will compare some uninitialized
memory. This triggers 'uninit-value' issue.

This patch will add 'memcpy_from_msg' possible errors processing to
avoid uninit-value issue.

Tested via syzkaller

## References
- https://git.kernel.org/stable/c/2b4c99f7d9a57ecd644eda9b1fb0a1072414959f
- https://git.kernel.org/stable/c/2e6ad51c709fa794e0ce26003c9c9cd944e3383a
- https://git.kernel.org/stable/c/3fa0f1e0e31b1b73cdf59d4c36c7242e6ef821be
- https://git.kernel.org/stable/c/618b15d09fed6126356101543451d49860db4388
- https://git.kernel.org/stable/c/78bc7f0ab99458221224d3ab97199c0f8e6861f1
- https://git.kernel.org/stable/c/ab2a55907823f0bca56b6d03ea05e4071ba8535f
- https://git.kernel.org/stable/c/bf70e0eab64c625da84d9fdf4e84466b79418920
- https://git.kernel.org/stable/c/c11dbc7705b3739974ac31a13f4ab81e61a5fb07
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53344.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53344
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
