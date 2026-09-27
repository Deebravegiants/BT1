# [H] net/sched: sch_teql: Introduce slaves_lock to avoid race condition and UAF

## Summary
Severity: High
Advisory: CVE-2026-72390
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72390
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: sch_teql: Introduce slaves_lock to avoid race condition and UAF

The teql master->slaves singly linked list is not protected against
multiple writes. It can be mod'ed concurently from teql_master_xmit(),
teql_dequeue(), teql_init() and teql_destroy() without holding any list
lock or RCU protection.

zdi-disclosures@trendmicro.com has demonstrated that the qdisc is freed
after an RCU grace period, but teql_master_xmit() running on another
CPU can still hold a stale pointer into the list, resulting in a
slab-use-after-free:

BUG: KASAN: slab-use-after-free in teql_master_xmit+0xf0f/0x16b0
Read of size 8 at addr ffff888013fb0440 by task poc/332
Freed 512-byte region [ffff888013fb0400, ffff888013fb0600) (kmalloc-512)

The fix?
Add a per-master slaves_lock spinlock that serializes all mutations of
master->slaves and the NEXT_SLAVE() links in teql_destroy() and
teql_qdisc_init(). teql_master_xmit() also takes the same slaves_lock
around those updates.
Annotate master->slaves and the per-slave ->next pointer with __rcu and
use the appropriate RCU accessors everywhere they are touched:
rcu_assign_pointer() on the writer side (under slaves_lock),
rcu_dereference_protected() for the writer-side loads (also under
slaves_lock), rcu_dereference_bh() for the loads in teql_master_xmit() and
rtnl_dereference() for the loads in teql_master_open()/teql_master_mtu(),
which run under RTNL.
Pair this with rcu_read_lock_bh()/rcu_read_unlock_bh() around the list
traversal in teql_master_xmit(), so that readers either observe a fully
linked list or are deferred until the in-flight mutation completes. The two
early-return paths in teql_master_xmit() are updated to release the RCU-bh
read-side critical section before returning, since leaving it held would
disable BH on that CPU for good.

## References
- https://git.kernel.org/stable/c/03c67781254c574ae7fa75e881239a78473bdf42
- https://git.kernel.org/stable/c/11402e6e18e96df615cbcc58157818dd604b23ff
- https://git.kernel.org/stable/c/735567bde7401f82b064f9f107b52ee1bf84ed8c
- https://git.kernel.org/stable/c/9b7d05cbaa60108642402100efa6aa288dd33023
- https://git.kernel.org/stable/c/b26aa9d993537a4c3167d8ceead3b7c69c3a0aac
- https://git.kernel.org/stable/c/e5b811fe793166aecc59b085c1b7c31262ef2316
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72390.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72390
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
