# [H] ipv6: fix race condition between ipv6_get_ifaddr and ipv6_del_addr

## Summary
Severity: High
Advisory: CVE-2024-35969
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/CVE-2024-35969
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <4.19.313, >=4.20.0 <5.4.275, >=5.5.0 <5.10.216, >=5.11.0 <5.15.156, >=5.16.0 <6.1.87, >=6.2.0 <6.6.28, >=6.7.0 <6.8.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: fix race condition between ipv6_get_ifaddr and ipv6_del_addr

Although ipv6_get_ifaddr walks inet6_addr_lst under the RCU lock, it
still means hlist_for_each_entry_rcu can return an item that got removed
from the list. The memory itself of such item is not freed thanks to RCU
but nothing guarantees the actual content of the memory is sane.

In particular, the reference count can be zero. This can happen if
ipv6_del_addr is called in parallel. ipv6_del_addr removes the entry
from inet6_addr_lst (hlist_del_init_rcu(&ifp->addr_lst)) and drops all
references (__in6_ifa_put(ifp) + in6_ifa_put(ifp)). With bad enough
timing, this can happen:

1. In ipv6_get_ifaddr, hlist_for_each_entry_rcu returns an entry.

2. Then, the whole ipv6_del_addr is executed for the given entry. The
   reference count drops to zero and kfree_rcu is scheduled.

3. ipv6_get_ifaddr continues and tries to increments the reference count
   (in6_ifa_hold).

4. The rcu is unlocked and the entry is freed.

5. The freed entry is returned.

Prevent increasing of the reference count in such case. The name
in6_ifa_hold_safe is chosen to mimic the existing fib6_info_hold_safe.

[   41.506330] refcount_t: addition on 0; use-after-free.
[   41.506760] WARNING: CPU: 0 PID: 595 at lib/refcount.c:25 refcount_warn_saturate+0xa5/0x130
[   41.507413] Modules linked in: veth bridge stp llc
[   41.507821] CPU: 0 PID: 595 Comm: python3 Not tainted 6.9.0-rc2.main-00208-g49563be82afa #14
[   41.508479] Hardware name: QEMU Standard PC (i440FX + PIIX, 1996)
[   41.509163] RIP: 0010:refcount_warn_saturate+0xa5/0x130
[   41.509586] Code: ad ff 90 0f 0b 90 90 c3 cc cc cc cc 80 3d c0 30 ad 01 00 75 a0 c6 05 b7 30 ad 01 01 90 48 c7 c7 38 cc 7a 8c e8 cc 18 ad ff 90 <0f> 0b 90 90 c3 cc cc cc cc 80 3d 98 30 ad 01 00 0f 85 75 ff ff ff
[   41.510956] RSP: 0018:ffffbda3c026baf0 EFLAGS: 00010282
[   41.511368] RAX: 0000000000000000 RBX: ffff9e9c46914800 RCX: 0000000000000000
[   41.511910] RDX: ffff9e9c7ec29c00 RSI: ffff9e9c7ec1c900 RDI: ffff9e9c7ec1c900
[   41.512445] RBP: ffff9e9c43660c9c R08: 0000000000009ffb R09: 00000000ffffdfff
[   41.512998] R10: 00000000ffffdfff R11: ffffffff8ca58a40 R12: ffff9e9c4339a000
[   41.513534] R13: 0000000000000001 R14: ffff9e9c438a0000 R15: ffffbda3c026bb48
[   41.514086] FS:  00007fbc4cda1740(0000) GS:ffff9e9c7ec00000(0000) knlGS:0000000000000000
[   41.514726] CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
[   41.515176] CR2: 000056233b337d88 CR3: 000000000376e006 CR4: 0000000000370ef0
[   41.515713] DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
[   41.516252] DR3: 0000000000000000 DR6: 00000000fffe0ff0 DR7: 0000000000000400
[   41.516799] Call Trace:
[   41.517037]  <TASK>
[   41.517249]  ? __warn+0x7b/0x120
[   41.517535]  ? refcount_warn_saturate+0xa5/0x130
[   41.517923]  ? report_bug+0x164/0x190
[   41.518240]  ? handle_bug+0x3d/0x70
[   41.518541]  ? exc_invalid_op+0x17/0x70
[   41.520972]  ? asm_exc_invalid_op+0x1a/0x20
[   41.521325]  ? refcount_warn_saturate+0xa5/0x130
[   41.521708]  ipv6_get_ifaddr+0xda/0xe0
[   41.522035]  inet6_rtm_getaddr+0x342/0x3f0
[   41.522376]  ? __pfx_inet6_rtm_getaddr+0x10/0x10
[   41.522758]  rtnetlink_rcv_msg+0x334/0x3d0
[   41.523102]  ? netlink_unicast+0x30f/0x390
[   41.523445]  ? __pfx_rtnetlink_rcv_msg+0x10/0x10
[   41.523832]  netlink_rcv_skb+0x53/0x100
[   41.524157]  netlink_unicast+0x23b/0x390
[   41.524484]  netlink_sendmsg+0x1f2/0x440
[   41.524826]  __sys_sendto+0x1d8/0x1f0
[   41.525145]  __x64_sys_sendto+0x1f/0x30
[   41.525467]  do_syscall_64+0xa5/0x1b0
[   41.525794]  entry_SYSCALL_64_after_hwframe+0x72/0x7a
[   41.526213] RIP: 0033:0x7fbc4cfcea9a
[   41.526528] Code: d8 64 89 02 48 c7 c0 ff ff ff ff eb b8 0f 1f 00 f3 0f 1e fa 41 89 ca 64 8b 04 25 18 00 00 00 85 c0 75 15 b8 2c 00 00 00 0f 05 <48> 3d 00 f0 ff ff 77 7e c3 0f 1f 44 00 00 41 54 48 83 ec 30 44 89
[   41.527942] RSP: 002b:00007f
---truncated---

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/01b11a0566670612bd464a932e5ac2eae53d8652
- https://git.kernel.org/stable/c/3fb02ec57ead2891a2306af8c51a306bc5945e70
- https://git.kernel.org/stable/c/4b19e9507c275de0cfe61c24db69179dc52cf9fb
- https://git.kernel.org/stable/c/6cdb20c342cd0193d3e956e3d83981d0f438bb83
- https://git.kernel.org/stable/c/7633c4da919ad51164acbf1aa322cc1a3ead6129
- https://git.kernel.org/stable/c/b4b3b69a19016d4e7fbdbd1dbcc184915eb862e1
- https://git.kernel.org/stable/c/cca606e14264098cba65efa82790825dbf69e903
- https://git.kernel.org/stable/c/de76ae9ea1a6cf9e77fcec4f2df2904e26c23ceb
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35969.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35969
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
