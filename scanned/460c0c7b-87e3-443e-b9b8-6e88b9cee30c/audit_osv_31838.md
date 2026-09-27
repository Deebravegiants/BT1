# [H] geneve: Fix use-after-free in geneve_find_dev().

## Summary
Severity: High
Advisory: CVE-2025-21858
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-12
Source: https://osv.dev/vulnerability/CVE-2025-21858
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.130, >=6.2.0 <6.6.80, >=6.7.0 <6.12.17, >=6.13.0 <6.13.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

geneve: Fix use-after-free in geneve_find_dev().

syzkaller reported a use-after-free in geneve_find_dev() [0]
without repro.

geneve_configure() links struct geneve_dev.next to
net_generic(net, geneve_net_id)->geneve_list.

The net here could differ from dev_net(dev) if IFLA_NET_NS_PID,
IFLA_NET_NS_FD, or IFLA_TARGET_NETNSID is set.

When dev_net(dev) is dismantled, geneve_exit_batch_rtnl() finally
calls unregister_netdevice_queue() for each dev in the netns,
and later the dev is freed.

However, its geneve_dev.next is still linked to the backend UDP
socket netns.

Then, use-after-free will occur when another geneve dev is created
in the netns.

Let's call geneve_dellink() instead in geneve_destroy_tunnels().

[0]:
BUG: KASAN: slab-use-after-free in geneve_find_dev drivers/net/geneve.c:1295 [inline]
BUG: KASAN: slab-use-after-free in geneve_configure+0x234/0x858 drivers/net/geneve.c:1343
Read of size 2 at addr ffff000054d6ee24 by task syz.1.4029/13441

CPU: 1 UID: 0 PID: 13441 Comm: syz.1.4029 Not tainted 6.13.0-g0ad9617c78ac #24 dc35ca22c79fb82e8e7bc5c9c9adafea898b1e3d
Hardware name: linux,dummy-virt (DT)
Call trace:
 show_stack+0x38/0x50 arch/arm64/kernel/stacktrace.c:466 (C)
 __dump_stack lib/dump_stack.c:94 [inline]
 dump_stack_lvl+0xbc/0x108 lib/dump_stack.c:120
 print_address_description mm/kasan/report.c:378 [inline]
 print_report+0x16c/0x6f0 mm/kasan/report.c:489
 kasan_report+0xc0/0x120 mm/kasan/report.c:602
 __asan_report_load2_noabort+0x20/0x30 mm/kasan/report_generic.c:379
 geneve_find_dev drivers/net/geneve.c:1295 [inline]
 geneve_configure+0x234/0x858 drivers/net/geneve.c:1343
 geneve_newlink+0xb8/0x128 drivers/net/geneve.c:1634
 rtnl_newlink_create+0x23c/0x868 net/core/rtnetlink.c:3795
 __rtnl_newlink net/core/rtnetlink.c:3906 [inline]
 rtnl_newlink+0x1054/0x1630 net/core/rtnetlink.c:4021
 rtnetlink_rcv_msg+0x61c/0x918 net/core/rtnetlink.c:6911
 netlink_rcv_skb+0x1dc/0x398 net/netlink/af_netlink.c:2543
 rtnetlink_rcv+0x34/0x50 net/core/rtnetlink.c:6938
 netlink_unicast_kernel net/netlink/af_netlink.c:1322 [inline]
 netlink_unicast+0x618/0x838 net/netlink/af_netlink.c:1348
 netlink_sendmsg+0x5fc/0x8b0 net/netlink/af_netlink.c:1892
 sock_sendmsg_nosec net/socket.c:713 [inline]
 __sock_sendmsg net/socket.c:728 [inline]
 ____sys_sendmsg+0x410/0x6f8 net/socket.c:2568
 ___sys_sendmsg+0x178/0x1d8 net/socket.c:2622
 __sys_sendmsg net/socket.c:2654 [inline]
 __do_sys_sendmsg net/socket.c:2659 [inline]
 __se_sys_sendmsg net/socket.c:2657 [inline]
 __arm64_sys_sendmsg+0x12c/0x1c8 net/socket.c:2657
 __invoke_syscall arch/arm64/kernel/syscall.c:35 [inline]
 invoke_syscall+0x90/0x278 arch/arm64/kernel/syscall.c:49
 el0_svc_common+0x13c/0x250 arch/arm64/kernel/syscall.c:132
 do_el0_svc+0x54/0x70 arch/arm64/kernel/syscall.c:151
 el0_svc+0x4c/0xa8 arch/arm64/kernel/entry-common.c:744
 el0t_64_sync_handler+0x78/0x108 arch/arm64/kernel/entry-common.c:762
 el0t_64_sync+0x198/0x1a0 arch/arm64/kernel/entry.S:600

Allocated by task 13247:
 kasan_save_stack mm/kasan/common.c:47 [inline]
 kasan_save_track+0x30/0x68 mm/kasan/common.c:68
 kasan_save_alloc_info+0x44/0x58 mm/kasan/generic.c:568
 poison_kmalloc_redzone mm/kasan/common.c:377 [inline]
 __kasan_kmalloc+0x84/0xa0 mm/kasan/common.c:394
 kasan_kmalloc include/linux/kasan.h:260 [inline]
 __do_kmalloc_node mm/slub.c:4298 [inline]
 __kmalloc_node_noprof+0x2a0/0x560 mm/slub.c:4304
 __kvmalloc_node_noprof+0x9c/0x230 mm/util.c:645
 alloc_netdev_mqs+0xb8/0x11a0 net/core/dev.c:11470
 rtnl_create_link+0x2b8/0xb50 net/core/rtnetlink.c:3604
 rtnl_newlink_create+0x19c/0x868 net/core/rtnetlink.c:3780
 __rtnl_newlink net/core/rtnetlink.c:3906 [inline]
 rtnl_newlink+0x1054/0x1630 net/core/rtnetlink.c:4021
 rtnetlink_rcv_msg+0x61c/0x918 net/core/rtnetlink.c:6911
 netlink_rcv_skb+0x1dc/0x398 net/netlink/af_netlink.c:2543
 rtnetlink_rcv+0x34/0x50 net/core/rtnetlink.c:6938
 netlink_unicast_kernel net/netlink/af_n
---truncated---

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/3ce92ca990cfac88a87c61df3cc0b5880e688ecf
- https://git.kernel.org/stable/c/5a0538ac6826807d6919f6aecbb8996c2865af2c
- https://git.kernel.org/stable/c/788dbca056a8783ec063da3c9d49a3a71c76c283
- https://git.kernel.org/stable/c/904e746b2e7fa952ab8801b303ce826a63153d78
- https://git.kernel.org/stable/c/9593172d93b9f91c362baec4643003dc29802929
- https://git.kernel.org/stable/c/d5e86e27de0936f3cb0a299ce519d993e9cf3886
- https://git.kernel.org/stable/c/da9b0ae47f084014b1e4b3f31f70a0defd047ff3
- https://git.kernel.org/stable/c/f74f6560146714241c6e167b03165ee77a86e316
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21858.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21858
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
