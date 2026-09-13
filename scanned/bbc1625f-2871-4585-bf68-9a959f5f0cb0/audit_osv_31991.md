# [H] RDMA/core: Fix use-after-free when rename device name

## Summary
Severity: High
Advisory: CVE-2025-22085
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22085
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/core: Fix use-after-free when rename device name

Syzbot reported a slab-use-after-free with the following call trace:

==================================================================
BUG: KASAN: slab-use-after-free in nla_put+0xd3/0x150 lib/nlattr.c:1099
Read of size 5 at addr ffff888140ea1c60 by task syz.0.988/10025

CPU: 0 UID: 0 PID: 10025 Comm: syz.0.988
Not tainted 6.14.0-rc4-syzkaller-00859-gf77f12010f67 #0
Hardware name: Google Compute Engine, BIOS Google 02/12/2025
Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:94 [inline]
 dump_stack_lvl+0x241/0x360 lib/dump_stack.c:120
 print_address_description mm/kasan/report.c:408 [inline]
 print_report+0x16e/0x5b0 mm/kasan/report.c:521
 kasan_report+0x143/0x180 mm/kasan/report.c:634
 kasan_check_range+0x282/0x290 mm/kasan/generic.c:189
 __asan_memcpy+0x29/0x70 mm/kasan/shadow.c:105
 nla_put+0xd3/0x150 lib/nlattr.c:1099
 nla_put_string include/net/netlink.h:1621 [inline]
 fill_nldev_handle+0x16e/0x200 drivers/infiniband/core/nldev.c:265
 rdma_nl_notify_event+0x561/0xef0 drivers/infiniband/core/nldev.c:2857
 ib_device_notify_register+0x22/0x230 drivers/infiniband/core/device.c:1344
 ib_register_device+0x1292/0x1460 drivers/infiniband/core/device.c:1460
 rxe_register_device+0x233/0x350 drivers/infiniband/sw/rxe/rxe_verbs.c:1540
 rxe_net_add+0x74/0xf0 drivers/infiniband/sw/rxe/rxe_net.c:550
 rxe_newlink+0xde/0x1a0 drivers/infiniband/sw/rxe/rxe.c:212
 nldev_newlink+0x5ea/0x680 drivers/infiniband/core/nldev.c:1795
 rdma_nl_rcv_skb drivers/infiniband/core/netlink.c:239 [inline]
 rdma_nl_rcv+0x6dd/0x9e0 drivers/infiniband/core/netlink.c:259
 netlink_unicast_kernel net/netlink/af_netlink.c:1313 [inline]
 netlink_unicast+0x7f6/0x990 net/netlink/af_netlink.c:1339
 netlink_sendmsg+0x8de/0xcb0 net/netlink/af_netlink.c:1883
 sock_sendmsg_nosec net/socket.c:709 [inline]
 __sock_sendmsg+0x221/0x270 net/socket.c:724
 ____sys_sendmsg+0x53a/0x860 net/socket.c:2564
 ___sys_sendmsg net/socket.c:2618 [inline]
 __sys_sendmsg+0x269/0x350 net/socket.c:2650
 do_syscall_x64 arch/x86/entry/common.c:52 [inline]
 do_syscall_64+0xf3/0x230 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x77/0x7f
RIP: 0033:0x7f42d1b8d169
Code: ff ff c3 66 2e 0f 1f 84 00 00 00 00 00 0f 1f 40 00 48 89 f8 48 ...
RSP: 002b:00007f42d2960038 EFLAGS: 00000246 ORIG_RAX: 000000000000002e
RAX: ffffffffffffffda RBX: 00007f42d1da6320 RCX: 00007f42d1b8d169
RDX: 0000000000000000 RSI: 00004000000002c0 RDI: 000000000000000c
RBP: 00007f42d1c0e2a0 R08: 0000000000000000 R09: 0000000000000000
R10: 0000000000000000 R11: 0000000000000246 R12: 0000000000000000
R13: 0000000000000000 R14: 00007f42d1da6320 R15: 00007ffe399344a8
 </TASK>

Allocated by task 10025:
 kasan_save_stack mm/kasan/common.c:47 [inline]
 kasan_save_track+0x3f/0x80 mm/kasan/common.c:68
 poison_kmalloc_redzone mm/kasan/common.c:377 [inline]
 __kasan_kmalloc+0x98/0xb0 mm/kasan/common.c:394
 kasan_kmalloc include/linux/kasan.h:260 [inline]
 __do_kmalloc_node mm/slub.c:4294 [inline]
 __kmalloc_node_track_caller_noprof+0x28b/0x4c0 mm/slub.c:4313
 __kmemdup_nul mm/util.c:61 [inline]
 kstrdup+0x42/0x100 mm/util.c:81
 kobject_set_name_vargs+0x61/0x120 lib/kobject.c:274
 dev_set_name+0xd5/0x120 drivers/base/core.c:3468
 assign_name drivers/infiniband/core/device.c:1202 [inline]
 ib_register_device+0x178/0x1460 drivers/infiniband/core/device.c:1384
 rxe_register_device+0x233/0x350 drivers/infiniband/sw/rxe/rxe_verbs.c:1540
 rxe_net_add+0x74/0xf0 drivers/infiniband/sw/rxe/rxe_net.c:550
 rxe_newlink+0xde/0x1a0 drivers/infiniband/sw/rxe/rxe.c:212
 nldev_newlink+0x5ea/0x680 drivers/infiniband/core/nldev.c:1795
 rdma_nl_rcv_skb drivers/infiniband/core/netlink.c:239 [inline]
 rdma_nl_rcv+0x6dd/0x9e0 drivers/infiniband/core/netlink.c:259
 netlink_unicast_kernel net/netlink/af_netlink.c:1313 [inline]
 netlink_unicast+0x7f6/0x990 net/netlink/af_netlink.c:1339
 netlink_sendmsg+0x8de/0xcb0 net
---truncated---

## References
- https://git.kernel.org/stable/c/0d6460b9d2a3ee380940bdf47680751ef91cb88e
- https://git.kernel.org/stable/c/1d6a9e7449e2a0c1e2934eee7880ba8bd1e464cd
- https://git.kernel.org/stable/c/56ec8580be5174b2b9774066e60f1aad56d201db
- https://git.kernel.org/stable/c/edf6b543e81ba68c6dbac2499ab362098a5a9716
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22085.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22085
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
