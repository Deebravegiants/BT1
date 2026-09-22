# [M] vxlan: Fix uninit-value in vxlan_vnifilter_dump()

## Summary
Severity: Medium
Advisory: CVE-2025-21716
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21716
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

vxlan: Fix uninit-value in vxlan_vnifilter_dump()

KMSAN reported an uninit-value access in vxlan_vnifilter_dump() [1].

If the length of the netlink message payload is less than
sizeof(struct tunnel_msg), vxlan_vnifilter_dump() accesses bytes
beyond the message. This can lead to uninit-value access. Fix this by
returning an error in such situations.

[1]
BUG: KMSAN: uninit-value in vxlan_vnifilter_dump+0x328/0x920 drivers/net/vxlan/vxlan_vnifilter.c:422
 vxlan_vnifilter_dump+0x328/0x920 drivers/net/vxlan/vxlan_vnifilter.c:422
 rtnl_dumpit+0xd5/0x2f0 net/core/rtnetlink.c:6786
 netlink_dump+0x93e/0x15f0 net/netlink/af_netlink.c:2317
 __netlink_dump_start+0x716/0xd60 net/netlink/af_netlink.c:2432
 netlink_dump_start include/linux/netlink.h:340 [inline]
 rtnetlink_dump_start net/core/rtnetlink.c:6815 [inline]
 rtnetlink_rcv_msg+0x1256/0x14a0 net/core/rtnetlink.c:6882
 netlink_rcv_skb+0x467/0x660 net/netlink/af_netlink.c:2542
 rtnetlink_rcv+0x35/0x40 net/core/rtnetlink.c:6944
 netlink_unicast_kernel net/netlink/af_netlink.c:1321 [inline]
 netlink_unicast+0xed6/0x1290 net/netlink/af_netlink.c:1347
 netlink_sendmsg+0x1092/0x1230 net/netlink/af_netlink.c:1891
 sock_sendmsg_nosec net/socket.c:711 [inline]
 __sock_sendmsg+0x330/0x3d0 net/socket.c:726
 ____sys_sendmsg+0x7f4/0xb50 net/socket.c:2583
 ___sys_sendmsg+0x271/0x3b0 net/socket.c:2637
 __sys_sendmsg net/socket.c:2669 [inline]
 __do_sys_sendmsg net/socket.c:2674 [inline]
 __se_sys_sendmsg net/socket.c:2672 [inline]
 __x64_sys_sendmsg+0x211/0x3e0 net/socket.c:2672
 x64_sys_call+0x3878/0x3d90 arch/x86/include/generated/asm/syscalls_64.h:47
 do_syscall_x64 arch/x86/entry/common.c:52 [inline]
 do_syscall_64+0xd9/0x1d0 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

Uninit was created at:
 slab_post_alloc_hook mm/slub.c:4110 [inline]
 slab_alloc_node mm/slub.c:4153 [inline]
 kmem_cache_alloc_node_noprof+0x800/0xe80 mm/slub.c:4205
 kmalloc_reserve+0x13b/0x4b0 net/core/skbuff.c:587
 __alloc_skb+0x347/0x7d0 net/core/skbuff.c:678
 alloc_skb include/linux/skbuff.h:1323 [inline]
 netlink_alloc_large_skb+0xa5/0x280 net/netlink/af_netlink.c:1196
 netlink_sendmsg+0xac9/0x1230 net/netlink/af_netlink.c:1866
 sock_sendmsg_nosec net/socket.c:711 [inline]
 __sock_sendmsg+0x330/0x3d0 net/socket.c:726
 ____sys_sendmsg+0x7f4/0xb50 net/socket.c:2583
 ___sys_sendmsg+0x271/0x3b0 net/socket.c:2637
 __sys_sendmsg net/socket.c:2669 [inline]
 __do_sys_sendmsg net/socket.c:2674 [inline]
 __se_sys_sendmsg net/socket.c:2672 [inline]
 __x64_sys_sendmsg+0x211/0x3e0 net/socket.c:2672
 x64_sys_call+0x3878/0x3d90 arch/x86/include/generated/asm/syscalls_64.h:47
 do_syscall_x64 arch/x86/entry/common.c:52 [inline]
 do_syscall_64+0xd9/0x1d0 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

CPU: 0 UID: 0 PID: 30991 Comm: syz.4.10630 Not tainted 6.12.0-10694-gc44daa7e3c73 #29
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.16.3-3.fc41 04/01/2014

## References
- https://git.kernel.org/stable/c/1693d1fade71646a0731b6b213298cb443d186ea
- https://git.kernel.org/stable/c/5066293b9b7046a906eff60e3949a887ae185a43
- https://git.kernel.org/stable/c/a84d511165d6ba7f331b90ae6b6ce180ec534daa
- https://git.kernel.org/stable/c/cb1de9309a48cc5b771115781eec05075fd67039
- https://git.kernel.org/stable/c/f554bce488605d2f70e06eeab5e4d2448c813713
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21716.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21716
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
