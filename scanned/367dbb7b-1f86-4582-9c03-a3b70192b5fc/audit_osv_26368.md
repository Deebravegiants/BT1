# [M] net: openvswitch: fix flow memory leak in ovs_flow_cmd_new

## Summary
Severity: Medium
Advisory: CVE-2023-52977
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-52977
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.303 <4.14.306, >=4.19.270 <4.19.273, >=5.4.229 <5.4.232, >=5.10.163 <5.10.168, >=5.15.86 <5.15.93, >=6.1.2 <6.1.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: openvswitch: fix flow memory leak in ovs_flow_cmd_new

Syzkaller reports a memory leak of new_flow in ovs_flow_cmd_new() as it is
not freed when an allocation of a key fails.

BUG: memory leak
unreferenced object 0xffff888116668000 (size 632):
  comm "syz-executor231", pid 1090, jiffies 4294844701 (age 18.871s)
  hex dump (first 32 bytes):
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
  backtrace:
    [<00000000defa3494>] kmem_cache_zalloc include/linux/slab.h:654 [inline]
    [<00000000defa3494>] ovs_flow_alloc+0x19/0x180 net/openvswitch/flow_table.c:77
    [<00000000c67d8873>] ovs_flow_cmd_new+0x1de/0xd40 net/openvswitch/datapath.c:957
    [<0000000010a539a8>] genl_family_rcv_msg_doit+0x22d/0x330 net/netlink/genetlink.c:739
    [<00000000dff3302d>] genl_family_rcv_msg net/netlink/genetlink.c:783 [inline]
    [<00000000dff3302d>] genl_rcv_msg+0x328/0x590 net/netlink/genetlink.c:800
    [<000000000286dd87>] netlink_rcv_skb+0x153/0x430 net/netlink/af_netlink.c:2515
    [<0000000061fed410>] genl_rcv+0x24/0x40 net/netlink/genetlink.c:811
    [<000000009dc0f111>] netlink_unicast_kernel net/netlink/af_netlink.c:1313 [inline]
    [<000000009dc0f111>] netlink_unicast+0x545/0x7f0 net/netlink/af_netlink.c:1339
    [<000000004a5ee816>] netlink_sendmsg+0x8e7/0xde0 net/netlink/af_netlink.c:1934
    [<00000000482b476f>] sock_sendmsg_nosec net/socket.c:651 [inline]
    [<00000000482b476f>] sock_sendmsg+0x152/0x190 net/socket.c:671
    [<00000000698574ba>] ____sys_sendmsg+0x70a/0x870 net/socket.c:2356
    [<00000000d28d9e11>] ___sys_sendmsg+0xf3/0x170 net/socket.c:2410
    [<0000000083ba9120>] __sys_sendmsg+0xe5/0x1b0 net/socket.c:2439
    [<00000000c00628f8>] do_syscall_64+0x30/0x40 arch/x86/entry/common.c:46
    [<000000004abfdcf4>] entry_SYSCALL_64_after_hwframe+0x61/0xc6

To fix this the patch rearranges the goto labels to reflect the order of
object allocations and adds appropriate goto statements on the error
paths.

Found by Linux Verification Center (linuxtesting.org) with Syzkaller.

## References
- https://git.kernel.org/stable/c/0c598aed445eb45b0ee7ba405f7ece99ee349c30
- https://git.kernel.org/stable/c/1ac653cf886cdfc082708c82dc6ac6115cebd2ee
- https://git.kernel.org/stable/c/70154489f531587996f3e9d7cceeee65cff0001d
- https://git.kernel.org/stable/c/70d40674a549d498bd63d5432acf46205da1534b
- https://git.kernel.org/stable/c/af4e720bc00a2653f7b9df21755b9978b3d7f386
- https://git.kernel.org/stable/c/ed6c5e8caf55778500202775167e8ccdb1a030cb
- https://git.kernel.org/stable/c/f423c2efd51d7eb1d143c2be7eea233241d9bbbf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52977.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52977
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
