# [H] tipc: Check the bearer type before calling tipc_udp_nl_bearer_add()

## Summary
Severity: High
Advisory: CVE-2024-26663
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-02
Source: https://osv.dev/vulnerability/CVE-2024-26663
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <4.19.307, >=4.20.0 <5.4.269, >=5.5.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.78, >=6.2.0 <6.6.17, >=6.7.0 <6.7.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: Check the bearer type before calling tipc_udp_nl_bearer_add()

syzbot reported the following general protection fault [1]:

general protection fault, probably for non-canonical address 0xdffffc0000000010: 0000 [#1] PREEMPT SMP KASAN
KASAN: null-ptr-deref in range [0x0000000000000080-0x0000000000000087]
...
RIP: 0010:tipc_udp_is_known_peer+0x9c/0x250 net/tipc/udp_media.c:291
...
Call Trace:
 <TASK>
 tipc_udp_nl_bearer_add+0x212/0x2f0 net/tipc/udp_media.c:646
 tipc_nl_bearer_add+0x21e/0x360 net/tipc/bearer.c:1089
 genl_family_rcv_msg_doit+0x1fc/0x2e0 net/netlink/genetlink.c:972
 genl_family_rcv_msg net/netlink/genetlink.c:1052 [inline]
 genl_rcv_msg+0x561/0x800 net/netlink/genetlink.c:1067
 netlink_rcv_skb+0x16b/0x440 net/netlink/af_netlink.c:2544
 genl_rcv+0x28/0x40 net/netlink/genetlink.c:1076
 netlink_unicast_kernel net/netlink/af_netlink.c:1341 [inline]
 netlink_unicast+0x53b/0x810 net/netlink/af_netlink.c:1367
 netlink_sendmsg+0x8b7/0xd70 net/netlink/af_netlink.c:1909
 sock_sendmsg_nosec net/socket.c:730 [inline]
 __sock_sendmsg+0xd5/0x180 net/socket.c:745
 ____sys_sendmsg+0x6ac/0x940 net/socket.c:2584
 ___sys_sendmsg+0x135/0x1d0 net/socket.c:2638
 __sys_sendmsg+0x117/0x1e0 net/socket.c:2667
 do_syscall_x64 arch/x86/entry/common.c:52 [inline]
 do_syscall_64+0x40/0x110 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x63/0x6b

The cause of this issue is that when tipc_nl_bearer_add() is called with
the TIPC_NLA_BEARER_UDP_OPTS attribute, tipc_udp_nl_bearer_add() is called
even if the bearer is not UDP.

tipc_udp_is_known_peer() called by tipc_udp_nl_bearer_add() assumes that
the media_ptr field of the tipc_bearer has an udp_bearer type object, so
the function goes crazy for non-UDP bearers.

This patch fixes the issue by checking the bearer type before calling
tipc_udp_nl_bearer_add() in tipc_nl_bearer_add().

## References
- https://git.kernel.org/stable/c/0cd331dfd6023640c9669d0592bc0fd491205f87
- https://git.kernel.org/stable/c/19d7314f2fb9515bdaac9829d4d8eb34edd1fe95
- https://git.kernel.org/stable/c/24ec8f0da93b8a9fba11600be8a90f0d73fb46f1
- https://git.kernel.org/stable/c/3871aa01e1a779d866fa9dfdd5a836f342f4eb87
- https://git.kernel.org/stable/c/3d3a5b31b43515b5752ff282702ca546ec3e48b6
- https://git.kernel.org/stable/c/6f70f0b412458c622a12d4292782c8e92e210c2f
- https://git.kernel.org/stable/c/888e3524be87f3df9fa3c083484e4b62b3e3bb59
- https://git.kernel.org/stable/c/c1701ea85ef0ec7be6a1b36c7da69f572ed2fd12
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26663.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26663
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
