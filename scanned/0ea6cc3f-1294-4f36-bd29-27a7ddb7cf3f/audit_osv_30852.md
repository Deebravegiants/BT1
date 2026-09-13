# [H] tipc: Fix use-after-free of kernel socket in cleanup_bearer().

## Summary
Severity: High
Advisory: CVE-2024-56642
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56642
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.13.0 <6.1.120, >=5.16.0 <6.6.66, >=6.2.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: Fix use-after-free of kernel socket in cleanup_bearer().

syzkaller reported a use-after-free of UDP kernel socket
in cleanup_bearer() without repro. [0][1]

When bearer_disable() calls tipc_udp_disable(), cleanup
of the UDP kernel socket is deferred by work calling
cleanup_bearer().

tipc_exit_net() waits for such works to finish by checking
tipc_net(net)->wq_count.  However, the work decrements the
count too early before releasing the kernel socket,
unblocking cleanup_net() and resulting in use-after-free.

Let's move the decrement after releasing the socket in
cleanup_bearer().

[0]:
ref_tracker: net notrefcnt@000000009b3d1faf has 1/1 users at
     sk_alloc+0x438/0x608
     inet_create+0x4c8/0xcb0
     __sock_create+0x350/0x6b8
     sock_create_kern+0x58/0x78
     udp_sock_create4+0x68/0x398
     udp_sock_create+0x88/0xc8
     tipc_udp_enable+0x5e8/0x848
     __tipc_nl_bearer_enable+0x84c/0xed8
     tipc_nl_bearer_enable+0x38/0x60
     genl_family_rcv_msg_doit+0x170/0x248
     genl_rcv_msg+0x400/0x5b0
     netlink_rcv_skb+0x1dc/0x398
     genl_rcv+0x44/0x68
     netlink_unicast+0x678/0x8b0
     netlink_sendmsg+0x5e4/0x898
     ____sys_sendmsg+0x500/0x830

[1]:
BUG: KMSAN: use-after-free in udp_hashslot include/net/udp.h:85 [inline]
BUG: KMSAN: use-after-free in udp_lib_unhash+0x3b8/0x930 net/ipv4/udp.c:1979
 udp_hashslot include/net/udp.h:85 [inline]
 udp_lib_unhash+0x3b8/0x930 net/ipv4/udp.c:1979
 sk_common_release+0xaf/0x3f0 net/core/sock.c:3820
 inet_release+0x1e0/0x260 net/ipv4/af_inet.c:437
 inet6_release+0x6f/0xd0 net/ipv6/af_inet6.c:489
 __sock_release net/socket.c:658 [inline]
 sock_release+0xa0/0x210 net/socket.c:686
 cleanup_bearer+0x42d/0x4c0 net/tipc/udp_media.c:819
 process_one_work kernel/workqueue.c:3229 [inline]
 process_scheduled_works+0xcaf/0x1c90 kernel/workqueue.c:3310
 worker_thread+0xf6c/0x1510 kernel/workqueue.c:3391
 kthread+0x531/0x6b0 kernel/kthread.c:389
 ret_from_fork+0x60/0x80 arch/x86/kernel/process.c:147
 ret_from_fork_asm+0x11/0x20 arch/x86/entry/entry_64.S:244

Uninit was created at:
 slab_free_hook mm/slub.c:2269 [inline]
 slab_free mm/slub.c:4580 [inline]
 kmem_cache_free+0x207/0xc40 mm/slub.c:4682
 net_free net/core/net_namespace.c:454 [inline]
 cleanup_net+0x16f2/0x19d0 net/core/net_namespace.c:647
 process_one_work kernel/workqueue.c:3229 [inline]
 process_scheduled_works+0xcaf/0x1c90 kernel/workqueue.c:3310
 worker_thread+0xf6c/0x1510 kernel/workqueue.c:3391
 kthread+0x531/0x6b0 kernel/kthread.c:389
 ret_from_fork+0x60/0x80 arch/x86/kernel/process.c:147
 ret_from_fork_asm+0x11/0x20 arch/x86/entry/entry_64.S:244

CPU: 0 UID: 0 PID: 54 Comm: kworker/0:2 Not tainted 6.12.0-rc1-00131-gf66ebf37d69c #7 91723d6f74857f70725e1583cba3cf4adc716cfa
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS rel-1.16.3-0-ga6ed6b701f0a-prebuilt.qemu.org 04/01/2014
Workqueue: events cleanup_bearer

## References
- https://git.kernel.org/stable/c/4e69457f9dfae67435f3ccf29008768eae860415
- https://git.kernel.org/stable/c/650ee9a22d7a2de8999fac2d45983597a0c22359
- https://git.kernel.org/stable/c/6a2fa13312e51a621f652d522d7e2df7066330b6
- https://git.kernel.org/stable/c/d00d4470bf8c4282617a3a10e76b20a9c7e4cffa
- https://git.kernel.org/stable/c/d2a4894f238551eae178904e7f45af87577074fd
- https://git.kernel.org/stable/c/d62d5180c036eeac09f80660edc7a602b369125f
- https://git.kernel.org/stable/c/e48b211c4c59062cb6dd6c2c37c51a7cc235a464
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56642.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56642
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
