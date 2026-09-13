# [H] netfilter: ipset: fix refcount race between list:set GC and swap

## Summary
Severity: High
Advisory: CVE-2026-74748
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-74748
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ipset: fix refcount race between list:set GC and swap

__ip_set_put_byindex() resolved the index to a set pointer under RCU,
then took ip_set_ref_lock in __ip_set_put() to decrement set->ref.
ip_set_swap() holds that same lock while swapping both the ip_set_list
slots and the two sets' ref counters, so it can interleave between the
dereference and the lock acquisition, leaving the caller to decrement a
set whose reference already moved to the other index and hit
BUG_ON(set->ref == 0). list_set_gc() reaches this from timer softirq,
which the nfnl mutex does not serialize against swap: an expiring
list:set member calls list_set_del() -> ip_set_put_byindex() while
IPSET_CMD_SWAP runs on the referenced sets.

Resolve the index and decrement under ip_set_ref_lock, as ip_set_swap()
already does, keeping the refcount tied to the index rather than to a
stale set pointer.

  kernel BUG at net/netfilter/ipset/ip_set_core.c:685!
  Oops: invalid opcode: 0000 [#1] SMP KASAN NOPTI
  RIP: 0010:ip_set_put_byindex (net/netfilter/ipset/ip_set_core.c:870)
  Call Trace:
   <IRQ>
   list_set_del (net/netfilter/ipset/ip_set_list_set.c:159)
   set_cleanup_entries (net/netfilter/ipset/ip_set_list_set.c:181)
   list_set_gc (net/netfilter/ipset/ip_set_list_set.c:578)
   call_timer_fn (kernel/time/timer.c:1748)
   __run_timers (kernel/time/timer.c:1799 kernel/time/timer.c:2374)
   run_timer_softirq (kernel/time/timer.c:2405)
   </IRQ>
  Kernel panic - not syncing: Fatal exception in interrupt

## References
- https://git.kernel.org/stable/c/0c88868271653537ed443272dd8e7d13634d214b
- https://git.kernel.org/stable/c/20cb13a523f0a05cb2d0a7d72abae687683712e0
- https://git.kernel.org/stable/c/24ffcb1e1688c55fd2a505f064295cd28eac546d
- https://git.kernel.org/stable/c/97a01de0c6321b7210d30d0a4d60f10f561097c7
- https://git.kernel.org/stable/c/b0aab9dd1a348b99d75ff52765719d0cc2050630
- https://git.kernel.org/stable/c/b891e7a6bb06e0f6560e5932665ac660acd12225
- https://git.kernel.org/stable/c/c21afc7c216a4d257a4f3f300e0791890bc846b9
- https://git.kernel.org/stable/c/cb20da33839f28f590c99f16bafaa6151451c0e8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74748.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74748
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
