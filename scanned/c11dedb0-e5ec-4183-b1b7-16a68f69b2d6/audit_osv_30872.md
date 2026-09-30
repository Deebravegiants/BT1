# [H] wifi: nl80211: fix NL80211_ATTR_MLO_LINK_ID off-by-one

## Summary
Severity: High
Advisory: CVE-2024-56663
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56663
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.121, >=6.2.0 <6.6.67, >=6.7.0 <6.12.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: nl80211: fix NL80211_ATTR_MLO_LINK_ID off-by-one

Since the netlink attribute range validation provides inclusive
checking, the *max* of attribute NL80211_ATTR_MLO_LINK_ID should be
IEEE80211_MLD_MAX_NUM_LINKS - 1 otherwise causing an off-by-one.

One crash stack for demonstration:
==================================================================
BUG: KASAN: wild-memory-access in ieee80211_tx_control_port+0x3b6/0xca0 net/mac80211/tx.c:5939
Read of size 6 at addr 001102080000000c by task fuzzer.386/9508

CPU: 1 PID: 9508 Comm: syz.1.386 Not tainted 6.1.70 #2
Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:88 [inline]
 dump_stack_lvl+0x177/0x231 lib/dump_stack.c:106
 print_report+0xe0/0x750 mm/kasan/report.c:398
 kasan_report+0x139/0x170 mm/kasan/report.c:495
 kasan_check_range+0x287/0x290 mm/kasan/generic.c:189
 memcpy+0x25/0x60 mm/kasan/shadow.c:65
 ieee80211_tx_control_port+0x3b6/0xca0 net/mac80211/tx.c:5939
 rdev_tx_control_port net/wireless/rdev-ops.h:761 [inline]
 nl80211_tx_control_port+0x7b3/0xc40 net/wireless/nl80211.c:15453
 genl_family_rcv_msg_doit+0x22e/0x320 net/netlink/genetlink.c:756
 genl_family_rcv_msg net/netlink/genetlink.c:833 [inline]
 genl_rcv_msg+0x539/0x740 net/netlink/genetlink.c:850
 netlink_rcv_skb+0x1de/0x420 net/netlink/af_netlink.c:2508
 genl_rcv+0x24/0x40 net/netlink/genetlink.c:861
 netlink_unicast_kernel net/netlink/af_netlink.c:1326 [inline]
 netlink_unicast+0x74b/0x8c0 net/netlink/af_netlink.c:1352
 netlink_sendmsg+0x882/0xb90 net/netlink/af_netlink.c:1874
 sock_sendmsg_nosec net/socket.c:716 [inline]
 __sock_sendmsg net/socket.c:728 [inline]
 ____sys_sendmsg+0x5cc/0x8f0 net/socket.c:2499
 ___sys_sendmsg+0x21c/0x290 net/socket.c:2553
 __sys_sendmsg net/socket.c:2582 [inline]
 __do_sys_sendmsg net/socket.c:2591 [inline]
 __se_sys_sendmsg+0x19e/0x270 net/socket.c:2589
 do_syscall_x64 arch/x86/entry/common.c:51 [inline]
 do_syscall_64+0x45/0x90 arch/x86/entry/common.c:81
 entry_SYSCALL_64_after_hwframe+0x63/0xcd

Update the policy to ensure correct validation.

## References
- https://git.kernel.org/stable/c/29e640ae641b9f5ffc666049426d2b16c98d9963
- https://git.kernel.org/stable/c/2e3dbf938656986cce73ac4083500d0bcfbffe24
- https://git.kernel.org/stable/c/f3412522f78826fef1dfae40ef378a863df2591c
- https://git.kernel.org/stable/c/f850d1d9f1106f528dfc5807565f2d1fa9a397d3
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56663.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56663
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
