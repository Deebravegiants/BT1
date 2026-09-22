# [H] tipc: Change nla_policy for bearer-related names to NLA_NUL_STRING

## Summary
Severity: High
Advisory: CVE-2023-52845
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52845
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <4.14.330, >=4.15.0 <4.19.299, >=4.20.0 <5.4.261, >=5.5.0 <5.10.201, >=5.11.0 <5.15.139, >=5.16.0 <6.1.63, >=6.2.0 <6.5.12, >=6.6.0 <6.6.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: Change nla_policy for bearer-related names to NLA_NUL_STRING

syzbot reported the following uninit-value access issue [1]:

=====================================================
BUG: KMSAN: uninit-value in strlen lib/string.c:418 [inline]
BUG: KMSAN: uninit-value in strstr+0xb8/0x2f0 lib/string.c:756
 strlen lib/string.c:418 [inline]
 strstr+0xb8/0x2f0 lib/string.c:756
 tipc_nl_node_reset_link_stats+0x3ea/0xb50 net/tipc/node.c:2595
 genl_family_rcv_msg_doit net/netlink/genetlink.c:971 [inline]
 genl_family_rcv_msg net/netlink/genetlink.c:1051 [inline]
 genl_rcv_msg+0x11ec/0x1290 net/netlink/genetlink.c:1066
 netlink_rcv_skb+0x371/0x650 net/netlink/af_netlink.c:2545
 genl_rcv+0x40/0x60 net/netlink/genetlink.c:1075
 netlink_unicast_kernel net/netlink/af_netlink.c:1342 [inline]
 netlink_unicast+0xf47/0x1250 net/netlink/af_netlink.c:1368
 netlink_sendmsg+0x1238/0x13d0 net/netlink/af_netlink.c:1910
 sock_sendmsg_nosec net/socket.c:730 [inline]
 sock_sendmsg net/socket.c:753 [inline]
 ____sys_sendmsg+0x9c2/0xd60 net/socket.c:2541
 ___sys_sendmsg+0x28d/0x3c0 net/socket.c:2595
 __sys_sendmsg net/socket.c:2624 [inline]
 __do_sys_sendmsg net/socket.c:2633 [inline]
 __se_sys_sendmsg net/socket.c:2631 [inline]
 __x64_sys_sendmsg+0x307/0x490 net/socket.c:2631
 do_syscall_x64 arch/x86/entry/common.c:50 [inline]
 do_syscall_64+0x41/0xc0 arch/x86/entry/common.c:80
 entry_SYSCALL_64_after_hwframe+0x63/0xcd

Uninit was created at:
 slab_post_alloc_hook+0x12f/0xb70 mm/slab.h:767
 slab_alloc_node mm/slub.c:3478 [inline]
 kmem_cache_alloc_node+0x577/0xa80 mm/slub.c:3523
 kmalloc_reserve+0x13d/0x4a0 net/core/skbuff.c:559
 __alloc_skb+0x318/0x740 net/core/skbuff.c:650
 alloc_skb include/linux/skbuff.h:1286 [inline]
 netlink_alloc_large_skb net/netlink/af_netlink.c:1214 [inline]
 netlink_sendmsg+0xb34/0x13d0 net/netlink/af_netlink.c:1885
 sock_sendmsg_nosec net/socket.c:730 [inline]
 sock_sendmsg net/socket.c:753 [inline]
 ____sys_sendmsg+0x9c2/0xd60 net/socket.c:2541
 ___sys_sendmsg+0x28d/0x3c0 net/socket.c:2595
 __sys_sendmsg net/socket.c:2624 [inline]
 __do_sys_sendmsg net/socket.c:2633 [inline]
 __se_sys_sendmsg net/socket.c:2631 [inline]
 __x64_sys_sendmsg+0x307/0x490 net/socket.c:2631
 do_syscall_x64 arch/x86/entry/common.c:50 [inline]
 do_syscall_64+0x41/0xc0 arch/x86/entry/common.c:80
 entry_SYSCALL_64_after_hwframe+0x63/0xcd

TIPC bearer-related names including link names must be null-terminated
strings. If a link name which is not null-terminated is passed through
netlink, strstr() and similar functions can cause buffer overrun. This
causes the above issue.

This patch changes the nla_policy for bearer-related names from NLA_STRING
to NLA_NUL_STRING. This resolves the issue by ensuring that only
null-terminated strings are accepted as bearer-related names.

syzbot reported similar uninit-value issue related to bearer names [2]. The
root cause of this issue is that a non-null-terminated bearer name was
passed. This patch also resolved this issue.

## References
- https://git.kernel.org/stable/c/19b3f72a41a8751e26bffc093bb7e1cef29ad579
- https://git.kernel.org/stable/c/2199260c42e6fbc5af8adae3bf78e623407c91b0
- https://git.kernel.org/stable/c/2426425d686b43adbc4f2f4a367b494f06f159d6
- https://git.kernel.org/stable/c/3907b89cd17fcc23e9a80789c36856f00ece0ba8
- https://git.kernel.org/stable/c/4c731e98fe4d678e87ba3e4d45d3cf0a5a193dc4
- https://git.kernel.org/stable/c/560992f41c0cea44b7603bc9e6c73bffbf6b5709
- https://git.kernel.org/stable/c/6744008c354bca2e4686a5b6056ee6b535d9f67d
- https://git.kernel.org/stable/c/abc1582119e8c4af14cedb0db6541fd603f45a04
- https://git.kernel.org/stable/c/b33d130f07f1decd756b849ab03c23d11d4dd294
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52845.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52845
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
