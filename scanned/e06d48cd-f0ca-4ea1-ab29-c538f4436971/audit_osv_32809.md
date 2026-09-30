# [H] RDMA/core: Fix "KASAN: slab-use-after-free Read in ib_register_device" problem

## Summary
Severity: High
Advisory: CVE-2025-38022
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-38022
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.248, >=5.11.0 <6.1.160, >=5.16.0 <6.6.120, >=6.2.0 <6.12.30, >=6.7.0 <6.14.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/core: Fix "KASAN: slab-use-after-free Read in ib_register_device" problem

Call Trace:

 __dump_stack lib/dump_stack.c:94 [inline]
 dump_stack_lvl+0x116/0x1f0 lib/dump_stack.c:120
 print_address_description mm/kasan/report.c:408 [inline]
 print_report+0xc3/0x670 mm/kasan/report.c:521
 kasan_report+0xe0/0x110 mm/kasan/report.c:634
 strlen+0x93/0xa0 lib/string.c:420
 __fortify_strlen include/linux/fortify-string.h:268 [inline]
 get_kobj_path_length lib/kobject.c:118 [inline]
 kobject_get_path+0x3f/0x2a0 lib/kobject.c:158
 kobject_uevent_env+0x289/0x1870 lib/kobject_uevent.c:545
 ib_register_device drivers/infiniband/core/device.c:1472 [inline]
 ib_register_device+0x8cf/0xe00 drivers/infiniband/core/device.c:1393
 rxe_register_device+0x275/0x320 drivers/infiniband/sw/rxe/rxe_verbs.c:1552
 rxe_net_add+0x8e/0xe0 drivers/infiniband/sw/rxe/rxe_net.c:550
 rxe_newlink+0x70/0x190 drivers/infiniband/sw/rxe/rxe.c:225
 nldev_newlink+0x3a3/0x680 drivers/infiniband/core/nldev.c:1796
 rdma_nl_rcv_msg+0x387/0x6e0 drivers/infiniband/core/netlink.c:195
 rdma_nl_rcv_skb.constprop.0.isra.0+0x2e5/0x450
 netlink_unicast_kernel net/netlink/af_netlink.c:1313 [inline]
 netlink_unicast+0x53a/0x7f0 net/netlink/af_netlink.c:1339
 netlink_sendmsg+0x8d1/0xdd0 net/netlink/af_netlink.c:1883
 sock_sendmsg_nosec net/socket.c:712 [inline]
 __sock_sendmsg net/socket.c:727 [inline]
 ____sys_sendmsg+0xa95/0xc70 net/socket.c:2566
 ___sys_sendmsg+0x134/0x1d0 net/socket.c:2620
 __sys_sendmsg+0x16d/0x220 net/socket.c:2652
 do_syscall_x64 arch/x86/entry/syscall_64.c:63 [inline]
 do_syscall_64+0xcd/0x260 arch/x86/entry/syscall_64.c:94
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

This problem is similar to the problem that the
commit 1d6a9e7449e2 ("RDMA/core: Fix use-after-free when rename device name")
fixes.

The root cause is: the function ib_device_rename() renames the name with
lock. But in the function kobject_uevent(), this name is accessed without
lock protection at the same time.

The solution is to add the lock protection when this name is accessed in
the function kobject_uevent().

## References
- https://git.kernel.org/stable/c/03df57ad4b0ff9c5a93ff981aba0b42578ad1571
- https://git.kernel.org/stable/c/10c7f1c647da3b77ef8827d974a97b6530b64df0
- https://git.kernel.org/stable/c/17d3103325e891e10994e7aa28d12bea04dc2c60
- https://git.kernel.org/stable/c/312dae3499106ec8cb7442ada12be080aa9fbc3b
- https://git.kernel.org/stable/c/5629064f92f0de6d6b3572055cd35361c3ad953c
- https://git.kernel.org/stable/c/ba467b6870ea2a73590478d9612d6ea1dcdd68b7
- https://git.kernel.org/stable/c/d0706bfd3ee40923c001c6827b786a309e2a8713
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38022.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38022
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
