# [H] rhashtable: clear stale iter->p on table restart

## Summary
Severity: High
Advisory: CVE-2026-64563
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-64563
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

rhashtable: clear stale iter->p on table restart

rhashtable_walk_start_check() has two restart paths when resuming a walk.
When iter->walker.tbl is valid, it re-validates iter->p against the table
and sets iter->p = NULL if the object is gone.  When iter->walker.tbl is
NULL (table was freed during resize), it resets slot and skip but forgets
to clear iter->p.

rhashtable_walk_next() then dereferences the stale iter->p, reading
freed memory.  This is a use-after-free.

Any caller that does multi-fragment rhashtable walks across
walk_stop/walk_start boundaries is affected.  Concrete cases include
netlink_diag (__netlink_diag_dump in net/netlink/diag.c) and TIPC
(tipc_nl_sk_walk in net/tipc/socket.c).

Crash stack (netlink_diag):
  BUG: KASAN: slab-use-after-free in rhashtable_walk_next+0x365/0x3c0
  Read of size 8 at addr ffff88801a9d2438 (freed kmalloc-2k, offset 1080)
  Call Trace:
   rhashtable_walk_next+0x365/0x3c0 (lib/rhashtable.c:1016)
   __netlink_diag_dump+0x160/0x760 (net/netlink/diag.c:122)
   netlink_diag_dump+0xc2/0x240
   netlink_dump+0x5bc/0x1270
   netlink_recvmsg+0x7a3/0x980
   sock_recvmsg+0x1bc/0x200
   __sys_recvfrom+0x1d4/0x2c0

## References
- https://git.kernel.org/stable/c/042fda5c088015f18838e5c692659a7be60aeb26
- https://git.kernel.org/stable/c/0955b65c2b47c30b439e2cf1b1e375073aa0413a
- https://git.kernel.org/stable/c/3ff7c1dbf722cf3fa538672452ba182318e0fcc3
- https://git.kernel.org/stable/c/4169d9fb92f313ff8e7e83d733c1ecdcc93eebd3
- https://git.kernel.org/stable/c/8173f7e2ce67e6ca1d4763f3da14e5b01ce77456
- https://git.kernel.org/stable/c/a0406c40c6638c5ae50257db6297b2fba6c9ba16
- https://git.kernel.org/stable/c/ba510b5e9fe396497d31162acb579f210adfe6c8
- https://git.kernel.org/stable/c/c39643ad99fea749be50615550e8f0e6d6e60694
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64563.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64563
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
