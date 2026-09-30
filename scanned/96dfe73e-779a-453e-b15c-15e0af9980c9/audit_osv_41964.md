# [H] netfilter: ipset: fix race between dump and ip_set_list resize

## Summary
Severity: High
Advisory: CVE-2026-64189
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-64189
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ipset: fix race between dump and ip_set_list resize

The release path of ip_set_dump_do() and ip_set_dump_done() read
inst->ip_set_list via ip_set_ref_netlink(), a plain rcu_dereference_raw()
of the array pointer. These run from netlink_recvmsg() without the nfnl
mutex and without an RCU read-side critical section.

A concurrent ip_set_create() can grow the array: it publishes the new
array, calls synchronize_net() and then kvfree()s the old one. Since the
dump paths read the array outside any RCU reader, synchronize_net() does
not wait for them and the old array can be freed while they still index
into it, causing a use-after-free.

The dumped set itself stays pinned via set->ref_netlink, so only the
array load needs protecting. Take rcu_read_lock() around it, matching
ip_set_get_byname() and __ip_set_put_byindex().

  BUG: KASAN: slab-use-after-free in ip_set_dump_do (net/netfilter/ipset/ip_set_core.c:1697)
  Read of size 8 at addr ffff88800b5c4018 by task exploit/150
  Call Trace:
   ...
   kasan_report (mm/kasan/report.c:595)
   ip_set_dump_do (net/netfilter/ipset/ip_set_core.c:1697)
   netlink_dump (net/netlink/af_netlink.c:2325)
   netlink_recvmsg (net/netlink/af_netlink.c:1976)
   sock_recvmsg (net/socket.c:1159)
   __sys_recvfrom (net/socket.c:2315)
   ...
  Oops: general protection fault, probably for non-canonical address ... KASAN NOPTI
  KASAN: maybe wild-memory-access in range [0x02d6...d0-0x02d6...d7]
  RIP: 0010:ip_set_dump_do (net/netfilter/ipset/ip_set_core.c:1698)
  Kernel panic - not syncing: Fatal exception

## References
- https://git.kernel.org/stable/c/1bc67c3fc98e9fc07032cc56afcdbc690c47d11e
- https://git.kernel.org/stable/c/7cd9103283b26b917360ec99d7d2f2d761bcf1ab
- https://git.kernel.org/stable/c/81d54c766337b923eec26da0a13406760b091093
- https://git.kernel.org/stable/c/96fbafc20ebd9a613736c2998b89c539fe3042f5
- https://git.kernel.org/stable/c/a7a299277959683204d73333c32c092fd69327d4
- https://git.kernel.org/stable/c/e8a9976b61f1bc4aa7fd25fa26726dfdf2adf710
- https://git.kernel.org/stable/c/e8ee198bbc04a32d336e79160fde980e0235b39f
- https://git.kernel.org/stable/c/ff86ea9b7fdf70564e60436fbee68c96bc459943
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64189.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64189
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
