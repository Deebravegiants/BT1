# [H] net: qualcomm: rmnet: fix global oob in rmnet_policy

## Summary
Severity: High
Advisory: CVE-2024-26597
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-23
Source: https://osv.dev/vulnerability/CVE-2024-26597
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <4.19.306, >=4.20.0 <5.4.268, >=5.5.0 <5.10.209, >=5.11.0 <5.15.148, >=5.16.0 <6.1.75, >=6.2.0 <6.6.14, >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: qualcomm: rmnet: fix global oob in rmnet_policy

The variable rmnet_link_ops assign a *bigger* maxtype which leads to a
global out-of-bounds read when parsing the netlink attributes. See bug
trace below:

==================================================================
BUG: KASAN: global-out-of-bounds in validate_nla lib/nlattr.c:386 [inline]
BUG: KASAN: global-out-of-bounds in __nla_validate_parse+0x24af/0x2750 lib/nlattr.c:600
Read of size 1 at addr ffffffff92c438d0 by task syz-executor.6/84207

CPU: 0 PID: 84207 Comm: syz-executor.6 Tainted: G                 N 6.1.0 #3
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.13.0-1ubuntu1.1 04/01/2014
Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:88 [inline]
 dump_stack_lvl+0x8b/0xb3 lib/dump_stack.c:106
 print_address_description mm/kasan/report.c:284 [inline]
 print_report+0x172/0x475 mm/kasan/report.c:395
 kasan_report+0xbb/0x1c0 mm/kasan/report.c:495
 validate_nla lib/nlattr.c:386 [inline]
 __nla_validate_parse+0x24af/0x2750 lib/nlattr.c:600
 __nla_parse+0x3e/0x50 lib/nlattr.c:697
 nla_parse_nested_deprecated include/net/netlink.h:1248 [inline]
 __rtnl_newlink+0x50a/0x1880 net/core/rtnetlink.c:3485
 rtnl_newlink+0x64/0xa0 net/core/rtnetlink.c:3594
 rtnetlink_rcv_msg+0x43c/0xd70 net/core/rtnetlink.c:6091
 netlink_rcv_skb+0x14f/0x410 net/netlink/af_netlink.c:2540
 netlink_unicast_kernel net/netlink/af_netlink.c:1319 [inline]
 netlink_unicast+0x54e/0x800 net/netlink/af_netlink.c:1345
 netlink_sendmsg+0x930/0xe50 net/netlink/af_netlink.c:1921
 sock_sendmsg_nosec net/socket.c:714 [inline]
 sock_sendmsg+0x154/0x190 net/socket.c:734
 ____sys_sendmsg+0x6df/0x840 net/socket.c:2482
 ___sys_sendmsg+0x110/0x1b0 net/socket.c:2536
 __sys_sendmsg+0xf3/0x1c0 net/socket.c:2565
 do_syscall_x64 arch/x86/entry/common.c:50 [inline]
 do_syscall_64+0x3b/0x90 arch/x86/entry/common.c:80
 entry_SYSCALL_64_after_hwframe+0x63/0xcd
RIP: 0033:0x7fdcf2072359
Code: 28 00 00 00 75 05 48 83 c4 28 c3 e8 f1 19 00 00 90 48 89 f8 48 89 f7 48 89 d6 48 89 ca 4d 89 c2 4d 89 c8 4c 8b 4c 24 08 0f 05 <48> 3d 01 f0 ff ff 73 01 c3 48 c7 c1 b8 ff ff ff f7 d8 64 89 01 48
RSP: 002b:00007fdcf13e3168 EFLAGS: 00000246 ORIG_RAX: 000000000000002e
RAX: ffffffffffffffda RBX: 00007fdcf219ff80 RCX: 00007fdcf2072359
RDX: 0000000000000000 RSI: 0000000020000200 RDI: 0000000000000003
RBP: 00007fdcf20bd493 R08: 0000000000000000 R09: 0000000000000000
R10: 0000000000000000 R11: 0000000000000246 R12: 0000000000000000
R13: 00007fffbb8d7bdf R14: 00007fdcf13e3300 R15: 0000000000022000
 </TASK>

The buggy address belongs to the variable:
 rmnet_policy+0x30/0xe0

The buggy address belongs to the physical page:
page:0000000065bdeb3c refcount:1 mapcount:0 mapping:0000000000000000 index:0x0 pfn:0x155243
flags: 0x200000000001000(reserved|node=0|zone=2)
raw: 0200000000001000 ffffea00055490c8 ffffea00055490c8 0000000000000000
raw: 0000000000000000 0000000000000000 00000001ffffffff 0000000000000000
page dumped because: kasan: bad access detected

Memory state around the buggy address:
 ffffffff92c43780: f9 f9 f9 f9 00 00 00 02 f9 f9 f9 f9 00 00 00 07
 ffffffff92c43800: f9 f9 f9 f9 00 00 00 05 f9 f9 f9 f9 06 f9 f9 f9
>ffffffff92c43880: f9 f9 f9 f9 00 00 00 00 00 00 f9 f9 f9 f9 f9 f9
                                                 ^
 ffffffff92c43900: 00 00 00 00 00 00 00 00 07 f9 f9 f9 f9 f9 f9 f9
 ffffffff92c43980: 00 00 00 07 f9 f9 f9 f9 00 00 00 05 f9 f9 f9 f9

According to the comment of `nla_parse_nested_deprecated`, the maxtype
should be len(destination array) - 1. Hence use `IFLA_RMNET_MAX` here.

## References
- https://git.kernel.org/stable/c/02467ab8b404d80429107588e0f3425cf5fcd2e5
- https://git.kernel.org/stable/c/093dab655808207f7a9f54cf156240aeafc70590
- https://git.kernel.org/stable/c/17d06a5c44d8fd2e8e61bac295b09153496f87e1
- https://git.kernel.org/stable/c/2295c22348faf795e1ccdf618f6eb7afdb2f7447
- https://git.kernel.org/stable/c/3b5254862258b595662a0ccca6e9eeb88d6e7468
- https://git.kernel.org/stable/c/b33fb5b801c6db408b774a68e7c8722796b59ecc
- https://git.kernel.org/stable/c/c4734535034672f59f2652e1e0058c490da62a5c
- https://git.kernel.org/stable/c/ee1dc3bf86f2df777038506b139371a9add02534
- https://lists.debian.org/debian-lts-announce/2024/06/msg00016.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26597.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26597
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
